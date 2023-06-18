import obsws_python as obs

class ObsController:
    # TODO: autorecord, etc
    def __init__(self, enabled):
        self.enabled = enabled

    def Setup(self):
        if self.enabled:
            self.obs_client = obs.ReqClient(host='localhost', port=4455, password='')
            scenes = self.obs_client.get_scene_list()
            # TODO configurable scene/input names
            self.obs_client.set_current_program_scene('Waiting')

    def StartRecording(self):
        if self.enabled:
            # TODO start recording
            print("recording started")

    def StopRecording(self):
        if self.enabled:
            print("recording stopped")
            # TODO don't forget to save the recording name so we can move it later

    def SetScene(self, title):
        self.obs_client.set_current_program_scene(title)

    def UpdateMapTitle(self, title):
        settings = {}
        # TODO configurable scene/input names
        settings['Text'] = title
        self.obs_client.set_input_settings("Text", settings=settings)