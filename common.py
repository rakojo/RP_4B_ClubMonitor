from PyQt5.QtWidgets import QMessageBox
import configparser as cfg_parser

    # global variables
display_cfg_file = 'displays_config.txt'
    # constans
INSTRUMENT_CFG_FILE = 'instruments_config.txt'


# =============================================================================
# messagebox show message with OK button
# =============================================================================    

def messagebox(message):
    msgBox = QMessageBox()
    msgBox.setText(message)
    msgBox.exec()


# =============================================================================
# read_cfg read from configuration file
# =============================================================================    

def read_cfg(file, sect, param):
    config = cfg_parser.ConfigParser(inline_comment_prefixes="#")
    config.read(file)
    try:
        ret = config[sect][param]
    except:
        messagebox(r"'{}' or '{}' does not exist in configuretion file !".format(sect, param)
        )

    return ret


# =============================================================================
# write_cfg write to configuration file
# =============================================================================    

def write_cfg(file, sect, param, val):
    config = cfg_parser.ConfigParser(inline_comment_prefixes="#")
    config.read(file)
    config.set(sect, param, val)
    with open(file, 'w') as configfile:
        config.write(configfile)


# =============================================================================
# return config file section list
# =============================================================================    

def get_sections_cfg(file):
    config = cfg_parser.ConfigParser(inline_comment_prefixes="#")
    config.read(file)
    return config.sections()


