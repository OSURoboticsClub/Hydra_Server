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

async def run():
    # Init the drone
    drone = System()
    await drone.connect(system_address="udp://:14555")

    # Start the tasks
    asyncio.ensure_future(print_battery(drone))
    asyncio.ensure_future(print_gps_info(drone))
    asyncio.ensure_future(print_in_air(drone))
    asyncio.ensure_future(print_position(drone))

async def print_battery(drone):
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent}")


async def print_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")


async def print_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")


async def print_position(drone):
    async for position in drone.telemetry.position():
        print(position)

async def echo_server(reader, writer):
    while True:
        drone = System()
        await drone.connect(system_address="udp://:14555")
        print("hi")
        data = await reader.read(100)  # Max number of bytes to read
        if not data:
            break
        async for position in drone.telemetry.position():
            # data_out = b''
            # print(position.latitude_deg)
            tmp = str(position.latitude_deg)
            print(tmp)
            # data_out = str(position.latitude_deg.encode('utf-8'))
            writer.write(tmp.encode())
            await writer.drain()  # Flow control, see later
            # print("end")
    writer.close()

async def main(host, port):
        server = await asyncio.start_server(echo_server, host, port)
        await server.serve_forever()

asyncio.run(main('127.0.0.1', 5000))
