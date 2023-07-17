from shiny import App, render, ui, reactive, Inputs, Outputs, Session
from shiny.types import ImgData

import image_processing as ip

app_ui = ui.page_fluid(
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
            ui.input_checkbox_group(
                "state", "State", choices=["busy", "denoising_ended"]
            ),
            ui.input_select(
                "denoise_method",
                "Denoising method",
                choices={
                    "svd": "Singular Value Decomposition",
                    "fft": "Fast Fourier Transform",
                    "wavelet": "Wavelet Transform",
                },
            ),
            ui.panel_conditional(
                "input['state'].includes('busy')",
                ui.input_action_button("denoise", "Denoise"),
            ),
            ui.panel_conditional(
                "input['state'].includes('denoising_ended')",
                ui.download_button(
                    "download",
                    "Download",
                    filename="denoised_image.png",
                    data="denoised_img",
                ),
                # style="display: none;",
            ),
            width=2,
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    img_path = reactive.Value(None)
    denosing_ended = reactive.Value(False)
    denoised_img = reactive.Value(None)
    busy = reactive.Value(True)

    @output
    @render.image
    def out_img():
        if input.file() is not None:
            denosing_ended.set(False)
            img_path.set(input.file()[0]["datapath"])
            img = ImgData(
                src=img_path.get(), alt="Uploaded image", height="100%", width="auto"
            )
            return img

    @reactive.Effect
    @reactive.event(input.denoise)
    def denoise():
        if input.denoise_method() is not None and img_path.get() is not None:
            img = ip.ImageDenoising(img_path.get(), input.denoise_method())
            denoised_img.set(img.denoise())
            denosing_ended.set(True)

    @reactive.Effect
    @reactive.event(denosing_ended)
    def denoising_ended_effect():
        if denosing_ended.get():
            ui.update_checkbox_group("state", selected=["denoising_ended"])


app = App(app_ui, server)
