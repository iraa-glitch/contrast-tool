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

# Known layer-number calibration measurements from the workbook
calibration_points = {
    "Zeiss": [
        {"Layer number": 1.0, "Optical contrast (%)": 7.791342952, "Sample": "53"},
        {"Layer number": 2.0, "Optical contrast (%)": 15.56603774, "Sample": "53"},
        {"Layer number": 3.0, "Optical contrast (%)": 26.52743835, "Sample": "53"},
        {"Layer number": 1.0, "Optical contrast (%)": 9.777138749, "Sample": "61"},
        {"Layer number": 4.0, "Optical contrast (%)": 30.5520362, "Sample": "61"},
        {"Layer number": 5.0, "Optical contrast (%)": 41.35802469, "Sample": "61"},
    ],
    "Nikon": [
        {"Layer number": 1.0, "Optical contrast (%)": 9.632683658, "Sample": "53"},
        {"Layer number": 2.0, "Optical contrast (%)": 19.2646783, "Sample": "53"},
    ],
}

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

        st.write(
            f"Optical contrast: **{contrast:.3f}%**"
        )

        st.write(
            f"Calculated layer number: "
            f"**{calculated_layers:.3f}**"
        )

        st.success(
            f"Estimated layer number: "
            f"{estimated_layers} layers"
        )

        selected_points = calibration_points[microscope]

        highest_layer = max(
            max(point["Layer number"] for point in selected_points),
            calculated_layers,
            5.0
        )

        line_end = highest_layer + 0.5

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
                "Sample": "User measurement"
            }
        ]

        chart_spec = {
            "title": f"{microscope} calibration graph",
            "height": 400,
            "encoding": {
                "x": {
                    "field": "Layer number",
                    "type": "quantitative",
                    "title": "Layer number",
                    "scale": {"zero": True}
                },
                "y": {
                    "field": "Optical contrast (%)",
                    "type": "quantitative",
                    "title": "Optical contrast (%)",
                    "scale": {"zero": True}
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
                    "data": {"values": selected_points},
                    "mark": {
                        "type": "point",
                        "filled": True,
                        "color": "#4C78A8",
                        "size": 90
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
                                "title": "Known layers",
                                "format": ".1f"
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
                        "size": 230,
                        "stroke": "black",
                        "strokeWidth": 1
                    },
                    "encoding": {
                        "tooltip": [
                            {
                                "field": "Sample",
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
            "Blue dots: calibration data. "
            "Red dot: the user's measurement. "
            "Dashed line: monolayer-based calibration."
        )
