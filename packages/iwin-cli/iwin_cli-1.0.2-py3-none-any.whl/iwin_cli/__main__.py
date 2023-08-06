from iwin_cli.simulation import validate_simulation
from iwin_cli.classconfig import validate_class


from iwin_cli import __version__
import getopt, sys

def main():
    print(f'iWin 配置工具 - 版本 {__version__}')
    argumentList=sys.argv[1:]
    # Options
    options = "hs:c:"
    
    # Long options
    long_options = ["help", "simulation=", "class="]
    
    try:
        simulation_path = None
        class_xlsx = None
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
            # print(f'currentArgument:{currentArgument}=[{currentValue}]')
            if currentArgument in ("-h", "--help"):
                print ("\niwin-cli -s <Simulation配置文件夹路径> -c <班级数据的xlsx文件名>")
                return
                
            elif currentArgument in ("-s", "--simulation"):
                print ("Simulation配置文件夹路径: %s" % (currentValue))
                simulation_path = currentValue
                
            elif currentArgument in ("-c", "--class"):
                print (("班级数据的xlsx文件名： %s") % (currentValue))
                class_xlsx = currentValue
        if simulation_path is not None:
            validate_simulation(simulation_path)
        if class_xlsx is not None:
            validate_class(class_xlsx)
        
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))


if __name__ == "__main__":
    # print(f'\n{sys.argv[0]}')
    main()