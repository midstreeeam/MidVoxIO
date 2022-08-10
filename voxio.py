from src.parser import Parser


class Voxio():

    @staticmethod
    def vox_to_arr(fname):
        vox=Parser(fname).parse()
        return vox.to_list()
    
    @staticmethod
    def test(fname):
        Parser(fname).parse()