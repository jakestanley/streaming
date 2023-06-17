from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

def create_grid_view(data):
    app = QApplication([])
    window = QMainWindow()
    model = QStandardItemModel()
    selected_index = -1

    table_view = QTableView(window)
    table_view.setModel(model)
    window.setCentralWidget(table_view)

    for row in data:
        item = QStandardItem(row)
        item.setEditable(False)
        model.appendRow(item)

    def handle_double_click(index):
        selected_index = model.data(index, Qt.DisplayRole)
        window.close()

    table_view.doubleClicked.connect(handle_double_click)

    window.show()
    app.exec_()
    return selected_index

# Example usage:
data = ["Option 1", "Option 2", "Option 3"]
print(create_grid_view(data))