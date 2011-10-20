from subprocess import call
import os

def main():
    #os.environ['WHATTHE'] = "HELLO"
    call("source dude.sh;", shell=True)
    print os.environ.get("WHATTHE")
    

if __name__ == "__main__":
    main()

