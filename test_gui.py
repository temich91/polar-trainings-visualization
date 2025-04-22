import dearpygui.dearpygui as dpg
data = [
    ["14.04.25", 6500, "37:42", 160, "5:55/km", 488, "18h06m00s", 30, "L", 82],
    ["15.04.25", 7700, "41:33", 164, "5:47/km", 528, "17h33m00s", 20, "E", 83],
    ["16.04.25", 4220, "21:42", 166, "5:15/km", 282, "18h56m00s", 22, "E", 82]
]

COLUMN_LABELS = ["Date", "Distance", "Duration", "AvgHR", "AvgPace", "ccal", "StartTime", "Elevation", "Type", "Cadence"]

dpg.create_context()


with dpg.font_registry():
    default_font = dpg.add_font(file=f"fonts\CascadiaCode.ttf", size=20)

with dpg.window(tag="primary_window"):
    dpg.add_text("Data:")
    dpg.bind_font(default_font)

    with dpg.table(header_row=True, policy=dpg.mvTable_SizingStretchProp,
                   borders_innerH=True, borders_innerV=True, borders_outerH=True, borders_outerV=True):
        for col_label in COLUMN_LABELS:
            dpg.add_table_column(label=col_label)

        for i in range(len(data)):
            with dpg.table_row():
                for j in range(len(COLUMN_LABELS)):
                    dpg.add_text(data[i][j])

dpg.create_viewport(title="runrunrun", width=900, height=450)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("primary_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
