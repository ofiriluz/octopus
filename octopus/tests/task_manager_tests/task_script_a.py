import json
import time
import sys

if __name__ == "__main__":
    # Dummy test, print some things to the console and then print some json
    print("Hi friend")
    time.sleep(5)
    print(sys.argv[1])
    print('{"Test":"ABC"}')
