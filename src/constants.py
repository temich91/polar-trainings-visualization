# Polar Flow scraper:
FLOW_URL = "https://flow.polar.com"
DRIVER_FILENAME = "../msedgedriver.exe"
COOKIES_DIR = "../data"
ELEMENT_VISIBILITY_TIMEOUT = 3 # seconds
COOKIE_DECLINE_BTN_CLASS = "CybotCookiebotDialogBodyButtonDecline"
PERIOD_SWITCHER_CLASS = "select-component__value-container.select-component__value-container--has-value.css-1hwfws3"
MONTHS_SWITCHER_CLASS = "picker-switch__link.picker-switch-days"
YEARS_SWITCHER_CLASS = "picker-switch__link.picker-switch-months"
SWITCHER_LEFT_ARROW_CLASS = "icon.icon-arrow-left.picker-previous-button"
PREVIOUS_DATE_ARROW_CLASS = "daterangeselection__previous_range.btn.btn-icon"
SWITCHER_RIGHT_ARROW_CLASS = "icon.icon-arrow-right.picker-next-button"
KEEP_SIGNED_IN_ID = "checkbox_keep_me_signed_in"
COOKIES_DIALOG_ID = "CybotCookiebotDialogBodyUnderlay"
FIRST_YEAR = 2008
MONTHS = {1: "янв.", 2: "фев.", 3: "март", 4: "апр.", 5: "май", 6: "июнь",
          7: "июль", 8: "авг.", 9: "сент.", 10: "окт.", 11: "нояб.", 12: "дек."}

# CSV parser and database connector:
DB_NAME = "trainings.db"
DEFAULT_CSV_DIR = "../csv_export"

SUMMARY_COLS = ["Date",
                "Start time",
                "Duration",
                "Total distance (km)",
                "Average heart rate (bpm)",
                "Average pace (min/km)",
                "Max pace (min/km)",
                "Ascent (m)",
                "Descent (m)",
                "Calories",
                "Average cadence (rpm)"]

TELEMETRY_COLS = ["Time",
                  "HR (bpm)",
                  "Pace (min/km)",
                  "Cadence",
                  "Altitude (m)"]

NEW_SUMMARY_COLS = {"Start time": "start_datetime",
                    "Duration": "duration",
                    "Total distance (km)": "distance",
                    "Average heart rate (bpm)": "hr_avg",
                    "Average pace (min/km)": "pace_avg",
                    "Max pace (min/km)": "pace_max",
                    "Ascent (m)": "ascent",
                    "Descent (m)": "descent",
                    "Calories": "calories",
                    "Average cadence (rpm)": "cadence_avg"}

NEW_TELEMETRY_COLS = {"Time": "time",
                      "HR (bpm)": "hr",
                      "Pace (min/km)": "pace",
                      "Cadence": "cadence",
                      "Altitude (m)": "altitude"}

SUMMARY_FILL_VALUES = {"start_datetime": "00:00:00",
                       "duration": 0,
                       "distance": 0.0,
                       "hr_avg": 0,
                       "pace_avg": "00:00",
                       "pace_max": "00:00",
                       "ascent": 0,
                       "descent": 0,
                       "calories": 0,
                       "cadence_avg": 0}

TELEMETRY_FILL_VALUES = {"time": 0,
                         "hr": 0,
                         "pace": "00:00",
                         "cadence": 0,
                         "altitude": 0}
