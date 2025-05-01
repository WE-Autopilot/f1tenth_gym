from black_controller import Controller

from weap_util.weap_container import run

def main():
    controller = Controller()
    run(controller, "maps/map2","map2")

if __name__ == "__main__":
    main()