const gameloop = require('node-gameloop');
const util = require('util');

// Example override configuration
const configuration = {};

var session = null;                        // The Realtime server session object
let sessionTimeoutTimer = null;
const SESSION_TIMEOUT = 1 * 60 * 1000;

// server op codes (messages server sends)
const LOGICAL_PLAYER_OP_CODE = 100;

// client op codes (messages client sends)
const SCENE_READY_OP_CODE = 200;
const HOP_OP_CODE = 201;

///////////////////////////////////////////////////////////////////////////////
// Utility functions
///////////////////////////////////////////////////////////////////////////////

// This function takes a list of peers and sends the opcode and string to the peer
function SendStringToClient(peerIds, opCode, stringToSend) {
    session.getLogger().info("[app] SendStringToClient: peerIds = " + peerIds.toString() + " opCode = " + opCode + " stringToSend = " + stringToSend);

    let gameMessage = session.newTextGameMessage(opCode, session.getServerId(), stringToSend);
    let peerArrayLen = peerIds.length;

    for (let index = 0; index < peerArrayLen; ++index) {
        session.getLogger().info("[app] SendStringToClient: sendMessageT " + gameMessage.toString() + " " + peerIds[index].toString());
        session.sendMessage(gameMessage, peerIds[index]);
    }
}

///////////////////////////////////////////////////////////////////////////////
// Game code
///////////////////////////////////////////////////////////////////////////////

let players = [];
let logicalPlayerIDs = {};

///////////////////////////////////////////////////////////////////////////////
// App callbacks
///////////////////////////////////////////////////////////////////////////////

// Called when game server is initialized, is passed server object of current session
function init(_session) {
    session = _session;
    session.getLogger().info("[app] init(_session): ");
    session.getLogger().info(util.inspect(_session));
}

function onMessage(gameMessage) {
    session.getLogger().info("[app] onMessage(gameMessage): ");
    session.getLogger().info(util.inspect(gameMessage));

    // sender 0 is server so we don't process them 
    if (gameMessage.sender != 0) {
        let logicalSender = logicalPlayerIDs[gameMessage.sender];

        switch (gameMessage.opCode) {
            case SCENE_READY_OP_CODE:
                // Do nothing as both players just need to signal ready state
                break;

            case HOP_OP_CODE:
                // Forward the HOP_OP_CODE message to the other player
                let otherPlayer = (logicalSender === 0) ? 1 : 0;
                if (players[otherPlayer]) {
                    SendStringToClient([players[otherPlayer]], HOP_OP_CODE, gameMessage.contents);
                }
                break;

            default:
                session.getLogger().info("[warning] Unrecognized opCode in gameMessage");
        }
    }
}

// On Player Connect is called when a player has passed initial validation
// Return true if player should connect
function onPlayerConnect(player) {
    session.getLogger().info("[app] onPlayerConnect: " + player.peerId);

    // once a player connects it's fine to let the game session keep going
    // it will be killed once any client disconnects
    if (sessionTimeoutTimer != null) {
        clearTimeout(sessionTimeoutTimer);
        sessionTimeoutTimer = null;
    }

    if (players.length >= 2) {
        // max of two players so reject any additional connections
        return false;
    }
    return true;
}

// onPlayerAccepted is called when a player has connected and not rejected
// by onPlayerConnect. At this point it's possible to broadcast to the player
function onPlayerAccepted(player) {
    session.getLogger().info("[app] onPlayerAccepted: player.peerId = " + player.peerId);
    // store the ID. Note that the index the player is assigned will be sent
    // to the client and determines if they are "player 0" or "player 1" independent
    // of the peerId
    players.push(player.peerId);
    session.getLogger().info("[app] onPlayerAccepted: new contents of players array = " + players.toString());

    let logicalID = players.length - 1;
    session.getLogger().info("[app] onPlayerAccepted: logical ID = " + logicalID);

    logicalPlayerIDs[player.peerId] = logicalID;
    session.getLogger().info("[app] onPlayerAccepted: logicalPlayerIDs array = " + logicalPlayerIDs.toString());

    SendStringToClient([player.peerId], LOGICAL_PLAYER_OP_CODE, logicalID.toString());
}

// On Player Disconnect is called when a player has left or been forcibly terminated
// Is only called for players that actually connect to the server and not those rejected by validation
// This is called before the player is removed from the player list
function onPlayerDisconnect(peerId) {
    session.getLogger().info("[app] onPlayerDisconnect: " + peerId);
    StopGame();
}

function StopGame() {
    session.getLogger().info("[app] StopGame - ending game session");

    players = [];
    logicalPlayerIDs = {};

    if (session != null) {
        session.processEnding().then(function (outcome) {
            session.getLogger().info("Completed process ending with: " + outcome);
            process.exit(0);
        });
    }
}

// On Process Started is called when the process has begun and we need to perform any
// bootstrapping.  This is where the developer should insert any necessary code to prepare
// the process to be able to host a game session.
// Return true if the process has been appropriately prepared and it is okay to invoke the
// GameLift ProcessReady() call.
function onProcessStarted() {
    session.getLogger().info("Starting process...");
    session.getLogger().info("Ready to host games...");
    return true;
}

// On Start Game Session is called when GameLift creates a game session that runs this server script
// A Game Session is one instance of your game actually running. Each instance will have its
// own instance of this script.
function onStartGameSession(gameSession) {
    session.getLogger().info("[app] onStartGameSession");
    // The game session is started by the client service Lambda function
    // If no player joins, we want to kill the game session after
    // a certain period of time so it doesn't hang around forever taking up
    // a game instance.
    sessionTimeoutTimer = setTimeout(StopGame, SESSION_TIMEOUT);
}

exports.ssExports = {
    configuration: configuration,
    init: init,
    onMessage: onMessage,
    onPlayerConnect: onPlayerConnect,
    onPlayerDisconnect: onPlayerDisconnect,
    onProcessStarted: onProcessStarted,
    onPlayerAccepted: onPlayerAccepted,
    onStartGameSession: onStartGameSession
};
