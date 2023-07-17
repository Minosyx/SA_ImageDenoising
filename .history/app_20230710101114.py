from shiny import App, render, ui, reactive, Inputs, Outputs, Session
from shiny.types import ImgData
import asyncio

import image_processing as ip

app_ui = ui.page_fluid(
    ui.panel_title("Image denoising"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_file(
                "file", "Upload an image file", accept="image/*", multiple=False
            ),
            ui.input_checkbox_group(
                "state", "State", choices=["free", "denoising_ended"]
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
                "input['state'].includes('free')",
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
    img_name = reactive.Value(None)
    img_new_name = reactive.Value(None)
    denosing_ended = reactive.Value(False)
    denoised_img = reactive.Value(None)
    free = reactive.Value(True)

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
    @reactive.event(free)
    def free_effect():
        if free.get():
            active_state = list(input.state())
            active_state.append("free")
            ui.update_checkbox_group("state", selected=active_state)

    @session.download(
        "download",
        filename=img_new_name.get(),
        data=denoised_img.get(),
        media_type="image/*",
    )
    @reactive.Effect
    @reactive.event(denoised_img)
    async def download():
        await asyncio.sleep(0.1)


app = App(app_ui, server)
