from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QCheckBox, QGroupBox, QRadioButton, QDialogButtonBox, QLabel, QLineEdit
from PyQt5.QtCore import Qt

class OptionsDialog(QDialog):
    def __init__(self, parent=None, options=[]):
        super(OptionsDialog, self).__init__(parent)
        self.options = options
        self.setWindowTitle("Options")

        # build layout
        layout: QVBoxLayout = QVBoxLayout(self)

        # options: last
        checkbox_last = QCheckBox("Last")
        checkbox_last.setChecked(self.options.last)
        checkbox_last.stateChanged.connect(lambda state: self.set_last(state == Qt.Checked))
        layout.addWidget(checkbox_last)

        checkbox_last_label = QLabel("Play the previously selected map")
        layout.addWidget(checkbox_last_label)

        # options: obs
        checkbox_obs = QCheckBox("Control OBS")
        layout.addWidget(checkbox_obs)

        checkbox_obs_label = QLabel("If unchecked, recording and scene control will be unavailable")
        layout.addWidget(checkbox_obs_label)

        # options: auto-record 
        checkbox_auto_record = QCheckBox("Enable auto record")
        checkbox_auto_record.setChecked(self.options.auto_record)
        checkbox_auto_record.stateChanged.connect(lambda state: self.set_auto_record(state == Qt.Checked))
        layout.addWidget(checkbox_auto_record)

        checkbox_auto_record_label = QLabel("If checked, video recording be started, ended automatically \nand the outputted recording will be renamed")
        layout.addWidget(checkbox_auto_record_label)

        # options: re-record (currently not implemented)
        # checkbox_re_record = QCheckBox("re_record")
        # layout.addWidget(checkbox_re_record)

        # options: play scene
        groupbox_playscene = QGroupBox("Play scene")
        layout.addWidget(groupbox_playscene)

        playscene_layout = QVBoxLayout()
        groupbox_playscene.setLayout(playscene_layout)

        textfield_playscene = QLineEdit()
        textfield_playscene.setText(self.options.play_scene)
        textfield_playscene.textChanged.connect(lambda text: self.set_playscene(text))
        playscene_layout.addWidget(textfield_playscene)

        textfield_playscene_label = QLabel("Which scene should OBS switch to on game launch?")
        playscene_layout.addWidget(textfield_playscene_label)

        # options: QoL mods
        checkbox_no_qol = QCheckBox("Enable QoL mods")
        checkbox_no_qol.setChecked(not self.options.no_qol)
        checkbox_no_qol.stateChanged.connect(lambda state: self.set_qol(state == Qt.Checked))
        layout.addWidget(checkbox_no_qol)

        checkbox_no_qol_label = QLabel("If unchecked, any configured 'Quality of Life' mods \nwill not be included in the launch configuration")
        layout.addWidget(checkbox_no_qol_label)

        # options: Source port override TODO implement
        #groupbox_ports = QGroupBox("Source port")
        #checkbox_source_port = QCheckBox("Port")
        #layout.addWidget(checkbox_source_port)

        # options: crispy doom
        checkbox_crispy = QCheckBox("Prefer Crispy Doom")
        checkbox_crispy.setChecked(self.options.crispy)
        checkbox_crispy.stateChanged.connect(lambda state: self.set_crispy(state == Qt.Checked))
        layout.addWidget(checkbox_crispy)

        checkbox_crispy_label = QLabel("If playing a Chocolate Doom mod, force it to launch with Crispy Doom")
        layout.addWidget(checkbox_crispy_label)
        
        # options: random
        checkbox_random = QCheckBox("Random")
        checkbox_random.setChecked(self.options.random)
        checkbox_random.stateChanged.connect(lambda state: self.set_random(state == Qt.Checked))
        layout.addWidget(checkbox_random)

        checkbox_random_label = QLabel("Play a random map from the provided mod list")
        layout.addWidget(checkbox_random_label)

        # options: no demo
        checkbox_no_demo = QCheckBox("Record demo")
        checkbox_no_demo.setChecked(not self.options.no_demo)
        checkbox_no_demo.stateChanged.connect(lambda state: self.set_demo(state == Qt.Checked))
        layout.addWidget(checkbox_no_demo)

        checkbox_no_demo_label = QLabel("If unchecked, no demo lump will be created for this session")
        layout.addWidget(checkbox_no_demo_label)

        # options: save defaults TODO implement if you dare
        # checkbox_save_defaults = QCheckBox("Save defaults")

        # special controls
        checkbox_obs.setChecked(not self.options.no_obs)
        checkbox_obs.stateChanged.connect(lambda state: self.set_obs(state == Qt.Checked, [checkbox_auto_record, groupbox_playscene]))
        if (self.options.no_obs):
            checkbox_auto_record.setEnabled(False)
            groupbox_playscene.setEnabled(False)

        # confirm or close
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


    def set_last(self, value):
        self.options.last = value

    def set_obs(self, value, disables):
        self.options.no_obs = not value
        for disable in disables:
            disable.setEnabled(value)
        
    def set_playscene(self, value):
        self.options.play_scene = value

    def set_crispy(self, value):
        self.options.crispy = value

    def set_auto_record(self, value):
        self.options.auto_record = value

    def set_qol(self, value):
        self.options.no_qol = not value

    def set_random(self, value):
        self.options.random = value

    def set_demo(self, value):
        self.options.no_demo = not value

    def get_options(self):
        return self.options


def OpenOptionsGui(p_args):
    app = QApplication([])

    dialog = OptionsDialog(options=p_args)

    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_options()
    else:
        exit(0)