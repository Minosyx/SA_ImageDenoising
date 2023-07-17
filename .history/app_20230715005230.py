from shiny import App, render, ui, reactive, Inputs, Outputs, Session
from shiny.types import ImgData
import asyncio
import skimage
import shinyswatch

import image_processing as ip

import imageio.v3 as iio
import numpy as np
import io

app_ui = ui.page_fluid(
    shinyswatch.theme.darkly(),
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
            ui.panel_conditional(
                "false == true",
                ui.input_checkbox_group(
                    "state",
                    "State",
                    choices=["ready", "denoising_ended"],
                ),
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
            # ui.panel_conditional(
            #     "input['state'].includes('free')",
            ui.input_action_button("denoise", "Denoise", class_="btn-primary"),
            # ),
            # ui.panel_conditional(
            #     "input['state'].includes('denoising_ended')",
            ui.download_button(
                "download",
                "Download",
                filename="denoised_image.png",
                data="denoised_img",
                class_="btn-primary",
            ),
            # ),
            width=2,
        ),
        ui.panel_main(
            ui.output_image("out_img"),
        ),
    ),
    ui.tags.script(
        """
        $(document).on('shiny:connected', function(event) {
            Shiny.setInputValue('state', []);    
        });
        
        $(document).on('shiny:inputchanged', function(event) {
            if (event.name === 'state') {
                console.log(event.value);
                if (event.value.includes('ready')) {
                    $('#denoise').prop('disabled', false);
                } else {
                    $('#denoise').prop('disabled', true);
                }
                
                if (event.value.includes('denoising_ended')) {
                    $('#download').prop('disabled', false);
                } else {
                    $('#download').prop('disabled', true).prop("onclick", "return false;");
                }
            }
        });
        """
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    img_path = reactive.Value(None)
    img_name = reactive.Value(None)
    img_new_name = reactive.Value(None)
    denosing_ended = reactive.Value(False)
    denoised_img = reactive.Value(None)
    ready = reactive.Value(False)

    @reactive.Effect
    @reactive.event(input.file)
    def file():
        if input.file() is not None:
            img_name.set(input.file()[0]["name"])

    @output
    @render.image
    def out_img():
        if input.file() is not None:
            denosing_ended.set(False)
            ready.set(True)
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
            dimg = img.denoise()
            denosing_ended.set(True)
            denoised_img.set(dimg)

    @reactive.Effect
    @reactive.event(denosing_ended)
    def denoising_ended_effect():
        if denosing_ended.get():
            active_state = list(input.state())
            active_state.append("denoising_ended")

            denoising_method = input.denoise_method()
            base, ext = img_name.get().split(".")
            img_new_name.set(f"{base}_{denoising_method}.{ext}")

            ui.update_checkbox_group("state", selected=active_state)

    @reactive.Effect
    @reactive.event(ready)
    def ready_effect():
        if ready.get():
            active_state = list(input.state())
            active_state.append("ready")
            ui.update_checkbox_group("state", selected=active_state)

    @reactive.Effect
    @reactive.event(denoised_img)
    def download_prep():
        n_filename = img_new_name.get()
        n_ext = n_filename.split(".")[-1]

        @session.download(
            "download",
            filename=n_filename,
            media_type="image/*",
            encoding="binary",
        )
        async def download():
            img = denoised_img.get()
            with io.BytesIO() as output:
                iio.imwrite(output, img, extension=f".{n_ext}")
                # img.save(output, format=n_ext)
                yield output.getvalue()


app = App(app_ui, server)
