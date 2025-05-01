from black_controller import Controller as BlackController
from red_controller import Controller as RedController
from weap_util.weap_container import run

def main():
    controller = RedController()
    run(controller, "maps/map26","map26")

if __name__ == "__main__":
    main()