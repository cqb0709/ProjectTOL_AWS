import asyncio

# 클라이언트들의 소켓을 저장할 딕셔너리
clients = {}

# 서버 설정
HOST = '0.0.0.0'  # 모든 인터페이스에서 접속 허용
PORT = 12000      # 포트 설정

# 클라이언트 처리 코루틴
async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"새로운 연결: {client_address}")

    # 클라이언트를 딕셔너리에 추가
    clients[client_address] = (reader, writer)

    try:
        while True:
            # 클라이언트로부터 데이터 받기
            data = await reader.read(1024)
            if not data:
                break

            # 받은 데이터를 다른 클라이언트에게 모두 전송
            for player, (player_reader, player_writer) in clients.items():
                if player_writer != writer:  # 자신을 제외하고 보냄
                    player_writer.write(data)
                    await player_writer.drain()

    except (ConnectionResetError, OSError) as e:
        print(f"연결이 강제로 종료되었습니다: {client_address}, 에러: {e}")
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        if client_address in clients:
            del clients[client_address]
        try:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
        except (ConnectionResetError, OSError) as e:
            print(f"소켓을 닫는 중 에러 발생: {e}")
        except Exception as e:
            print(f"소켓을 닫는 중 알 수 없는 에러 발생: {e}")
        print(f"{client_address} 연결 종료")

# 클라이언트 접속을 처리하는 코루틴
async def handle_client_connection(reader, writer):
    await handle_client(reader, writer)

# 서버 시작 코루틴
async def start_server():
    server = await asyncio.start_server(handle_client_connection, HOST, PORT)
    print(f"서버 시작: {HOST}:{PORT}")
    async with server:
        await server.serve_forever()

# 비동기로 서버 시작
asyncio.run(start_server())
