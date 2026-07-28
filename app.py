import csv
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Optical Contrast Tool",
    page_icon="🔬"
)

st.title("Optical Contrast Tool")

calibrations = {
    "Zeiss": 7.791342952,
    "Nikon": 9.632683658
}

data_file = Path(__file__).with_name("calibration_data.csv")


@st.cache_data
def load_calibration_data():
    data = {"Zeiss": [], "Nikon": []}

    try:
        with data_file.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                microscope_name = row["microscope"]

                data[microscope_name].append({
                    "Sample": row["sample"],
                    "I_layer": float(row["i_layer"]),
                    "I_SiO2": float(row["i_sio2"]),
                    "Optical contrast (%)": float(row["contrast_percent"]),
                    "Calculated layer number": float(row["calculated_layer"]),
                    "Rounded layer number": int(row["rounded_layer"]),
                    "Is reference": int(row["is_reference"])
                })

    except FileNotFoundError:
        st.error(
            "The calibration_data.csv file is missing. "
            "Upload it to the same GitHub folder as app.py."
        )
        st.stop()

    return data


calibration_data = load_calibration_data()

microscope = st.selectbox(
    "Which microscope did you use?",
    ["Zeiss", "Nikon"]
)

i_layer = st.number_input(
    "Enter I_layer",
    min_value=0.0,
    format="%.6f"
)

i_sio2 = st.number_input(
    "Enter I_SiO2",
    min_value=0.0,
    format="%.6f"
)

if st.button("Calculate"):

    if i_sio2 == 0:
        st.error("I_SiO2 must be greater than zero.")

    else:
        delta_i = i_sio2 - i_layer
        contrast = (delta_i / i_sio2) * 100

        monolayer_contrast = calibrations[microscope]
        calculated_layers = contrast / monolayer_contrast
        estimated_layers = int(calculated_layers + 0.5)

        st.subheader("Results")

        st.write(f"ΔI: **{delta_i:.6f}**")
        st.write(f"Optical contrast: **{contrast:.3f}%**")

        st.write(
            f"Calculated layer number: "
            f"**{calculated_layers:.3f}**"
        )

        st.success(
            f"Estimated layer number: "
            f"{estimated_layers} layers"
        )

        all_points = calibration_data[microscope]

        measured_points = [
            {
                "Layer number": point["Rounded layer number"],
                "Optical contrast (%)": point["Optical contrast (%)"],
                "Sample": point["Sample"],
                "Calculated layer number": point["Calculated layer number"]
            }
            for point in all_points
            if point["Is reference"] == 0
        ]

        reference_points = [
            {
                "Layer number": 1.0,
                "Optical contrast (%)": point["Optical contrast (%)"],
                "Sample": point["Sample"],
                "Calculated layer number": point["Calculated layer number"]
            }
            for point in all_points
            if point["Is reference"] == 1
        ]

        maximum_layer = max(
            max(point["Rounded layer number"] for point in all_points),
            calculated_layers,
            5
        )

        line_end = maximum_layer + 0.5

        calibration_line = [
            {
                "Layer number": 0.0,
                "Optical contrast (%)": 0.0
            },
            {
                "Layer number": line_end,
                "Optical contrast (%)": monolayer_contrast * line_end
            }
        ]

        user_point = [
            {
                "Layer number": calculated_layers,
                "Optical contrast (%)": contrast,
                "Point": "User measurement"
            }
        ]

        chart_spec = {
            "title": f"{microscope} calibration graph",
            "height": 430,
            "encoding": {
                "x": {
                    "field": "Layer number",
                    "type": "quantitative",
                    "title": "Layer number",
                    "scale": {
                        "zero": True,
                        "domainMin": 0
                    }
                },
                "y": {
                    "field": "Optical contrast (%)",
                    "type": "quantitative",
                    "title": "Optical contrast (%)",
                    "scale": {
                        "zero": True,
                        "domainMin": 0
                    }
                }
            },
            "layer": [
                {
                    "data": {"values": calibration_line},
                    "mark": {
                        "type": "line",
                        "color": "gray",
                        "strokeDash": [6, 4],
                        "strokeWidth": 2
                    }
                },
                {
                    "data": {"values": measured_points},
                    "mark": {
                        "type": "point",
                        "filled": True,
                        "color": "#4C78A8",
                        "opacity": 0.48,
                        "size": 65
                    },
                    "encoding": {
                        "tooltip": [
                            {
                                "field": "Sample",
                                "type": "nominal",
                                "title": "Sample"
                            },
                            {
                                "field": "Layer number",
                                "type": "quantitative",
                                "title": "Nearest layer",
                                "format": ".0f"
                            },
                            {
                                "field": "Calculated layer number",
                                "type": "quantitative",
                                "title": "Decimal estimate",
                                "format": ".3f"
                            },
                            {
                                "field": "Optical contrast (%)",
                                "type": "quantitative",
                                "title": "Contrast (%)",
                                "format": ".3f"
                            }
                        ]
                    }
                },
                {
                    "data": {"values": reference_points},
                    "mark": {
                        "type": "point",
                        "shape": "diamond",
                        "filled": True,
                        "color": "#4C78A8",
                        "size": 230,
                        "stroke": "black",
                        "strokeWidth": 1
                    },
                    "encoding": {
                        "tooltip": [
                            {
                                "value": "Monolayer reference",
                                "type": "nominal",
                                "title": "Point"
                            },
                            {
                                "field": "Sample",
                                "type": "nominal",
                                "title": "Sample"
                            },
                            {
                                "field": "Optical contrast (%)",
                                "type": "quantitative",
                                "title": "Contrast (%)",
                                "format": ".3f"
                            }
                        ]
                    }
                },
                {
                    "data": {"values": user_point},
                    "mark": {
                        "type": "point",
                        "filled": True,
                        "color": "red",
                        "size": 280,
                        "stroke": "black",
                        "strokeWidth": 1
                    },
                    "encoding": {
                        "tooltip": [
                            {
                                "field": "Point",
                                "type": "nominal",
                                "title": "Point"
                            },
                            {
                                "field": "Layer number",
                                "type": "quantitative",
                                "title": "Calculated layers",
                                "format": ".3f"
                            },
                            {
                                "field": "Optical contrast (%)",
                                "type": "quantitative",
                                "title": "Contrast (%)",
                                "format": ".3f"
                            }
                        ]
                    }
                }
            ]
        }

        st.vega_lite_chart(
            chart_spec,
            use_container_width=True
        )

        st.caption(
            "Blue circles: measured samples grouped by the nearest estimated "
            "layer. Blue diamond: the monolayer reference. Red dot: the user's "
            "measurement. Dashed line: the monolayer-based calibration."
        )
