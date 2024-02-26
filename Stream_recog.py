import io
import socket
import struct
from PIL import Image
import cv2
import numpy
import pupil_apriltags as apriltag
import time
from scipy.spatial.transform import Rotation as R
import transforms3d
import pickle

import logging

camera_params = (506.19083684, 508.36108854,
                 317.93111342, 243.12403806)
tag_size = 0.0375

UDP_IP = "127.0.0.1"
UDP_PORT = 5065
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def record_loop(connection, server_socket):
    try:
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            print('to unpack')
            image_len = struct.unpack(
                '<L', connection.read(struct.calcsize('<L')))[0]
            print('I am here')
            if not image_len:
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            image = Image.open(image_stream)
            opencvImage = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            # Translate image to gray
            gray = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
            #blur = cv2.GaussianBlur(gray,(3,3),0)
            #_,otsu = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            cv2.imshow("gray", gray)
            cv2.imshow('Image', opencvImage)
            #cv2.imwrite(f'.\calibration\{i}.png',opencvImage)
            #out.write(opencvImage)
            image.verify()
    #        print('Image is verified')
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    finally:
        connection.close()
        print('Closing')
        server_socket.close()


def start_camera():
    logging.info('Begin')
    # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
    # all interfaces)
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)
    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('rb')

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('measuring_distance.mp4',fourcc,30,(640,480))
    record_loop(connection, server_socket)

