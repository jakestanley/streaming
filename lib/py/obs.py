import time
import obsws_python as obs
import os

class ObsController:
    def __init__(self, enabled):
        self.enabled = enabled

    def Setup(self):
        if self.enabled:
            try:
                self.obs_client = obs.ReqClient(host='localhost', port=4455, password='')
            except ConnectionRefusedError:
                print("""
    Unable to connect to OBS. Is it running? 
    Is the Websocket API enabled? 
    Should you have passed the --no-obs argument?
                    """)
                exit(1)
            scenes = self.obs_client.get_scene_list()
            # TODO configurable scene/input names
            self.obs_client.set_current_program_scene('Waiting')

    def IsRecording(self):
        return self.obs_client.get_record_status().output_active

    def StartRecording(self):
        if self.enabled:
            if self.IsRecording():
                self.StopRecording()
            self.obs_client.start_record()

    def StopRecording(self, name=None):
        if self.enabled:
            path = self.obs_client.stop_record().output_path
        else:
            return
        
        parent = os.path.dirname(path)
        ext = os.path.splitext(path)[1]
        newpath = f"{parent}/{name}{ext}"

        if not name == None:
            print(f"""
    Recording stopped
    Renaming '{path}' to 
    '{newpath}'
            """)

        # Pausing renaming for 5 seconds to allow OBS to release the handle
        time.sleep(5)
        
        os.rename(path, newpath)

    def SetScene(self, title):
        if self.enabled:
            self.obs_client.set_current_program_scene(title)
        else:
            print(f"OBS is disabled. Scene requested: '{title}'")

    def UpdateMapTitle(self, title):
        if self.enabled:
            settings = {}
            # TODO configurable scene/input names
            settings['Text'] = title
            self.obs_client.set_input_settings("Text Map Name", settings=settings, overlay=False)
        else:
            print(f"OBS is disabled. Title provided: '{title}'")
