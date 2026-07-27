
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
