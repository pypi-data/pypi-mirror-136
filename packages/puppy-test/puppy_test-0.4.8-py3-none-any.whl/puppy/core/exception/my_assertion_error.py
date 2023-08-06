from puppy.core.function.track.xml_track import xmlTrack


class MyAssertionError():

    def raise_error(self,msg):
        file_path,row=xmlTrack.current_path_row()
        msg='''\n  File "{}", line {}\n    raise\nAssertionError:{}'''.format(file_path,row,msg)
        raise AssertionError(msg)


