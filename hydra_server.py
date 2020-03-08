#!/usr/bin/env python3
"""
* Program: hydra_server.py
* Author: Tomas McMonigal
* Date: 2/15/2020
* Description: Multi-threaded server that accepts incoming connections to send
    telemetry data to GUI, CP, and PP programs. Receives telemetry data from
    ttyUSB0. To run it provide the port number as a command line parameter
"""
import asyncio
from mavsdk import System
from concurrent.futures import TimeoutError

async def echo_server(reader, writer, drone):

    while True:
            print("waiting on data requests")
            marker = 1

            try:
                data = await asyncio.wait_for(reader.read(100), timeout=3)
                if not data: # client has disconnected
                    print("connection closed by client: closing connection with client")
                    break
            except TimeoutError:
                print("Timeout error: closing connection with client")
                break

            # ******** if data is valid and connection active ****************
            data_in = data.decode() # decodes utf-8 only
            data_in = data_in.replace('\r\n', '')

            if data_in == "latitude":
                print("latitude requested")
                async for position in drone.telemetry.position():
                    data_out = str(position.latitude_deg) + '\n'
                    # data_out = data_out + '\n'
                    writer.write(data_out.encode())
                    await writer.drain()
                    break

            elif data_in == "altitude":
                async for position in drone.telemetry.position():
                    print("altitude requested")
                    data_out = str(position.relative_altitude_m) + '\n'
                    writer.write(data_out.encode())
                    await writer.drain()
                    break

            elif data_in == "longitude":
                async for position in drone.telemetry.position():
                    print("longitude requested")
                    data_out = str(position.longitude_deg) + '\n'
                    # data_out = data_out + '\n'
                    writer.write(data_out.encode())
                    await writer.drain()
                    break

            elif data_in == "battery":
                async for battery in drone.telemetry.battery():
                    print("battery percentage requested")
                    data_out = str(battery.voltage_v) + '\n'
                    writer.write(data_out.encode())
                    await writer.drain()
                    break

            elif data_in == "arm":
                print("-- Arming")
                await drone.action.arm()

            elif data_in == "disarm":
                print("-- Disarming")
                await drone.action.disarm()

            elif data_in == "kill":
                print("-- Killing")
                await drone.action.kill()

            else:
                print("error: data requested not supported, closing connection")
                output_string = '|' + data_in + '|'
                print(output_string)
    writer.close()

async def main(host, port):
    drone = System()
    await drone.connect(system_address="udp://:14555")
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered with UUID: {state.uuid}")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    print("Ready to accept incoming connections")
    server = await asyncio.start_server(lambda r, w: echo_server(r, w, drone), host, port)
    async with server:
        await server.serve_forever()

asyncio.run(main('127.0.0.1', 5000))
