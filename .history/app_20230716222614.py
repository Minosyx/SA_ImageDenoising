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
            ui.panel_conditional(
                "input['denoise_method'] == 'svd'",
                ui.input_slider(
                    "svd_k", "Number of singular values", min=1, max=10, step=1, value=5
                ),
                ui.input_numeric("svd_k_num", "", min=1, max=10, step=1, value=5),
            ),
            ui.panel_conditional(
                "input['denoise_method'] == 'fft'",
                ui.input_slider(
                    "fft_K",
                    "Size of the filtering kernel",
                    min=0,
                    max=10,
                    step=1,
                    value=5,
                ),
                ui.input_numeric("fft_K_num", "", min=0, max=10, step=1, value=5),
                ui.input_numeric(
                    "fft_percentile", "Percentile", min=0, max=100, step=1, value=98
                ),
            ),
            ui.panel_conditional(
                "input['denoise_method'] == 'wavelet'",
                ui.input_select(
                    "wavelet_method",
                    "Method",
                    choices={
                        "BayesShrink": "BayesShrink",
                        "VisuShrink": "VisuShrink",
                    },
                ),
                ui.input_select(
                    "wavelet_mode",
                    "Mode",
                    choices={
                        "soft": "Soft",
                        "hard": "Hard",
                    },
                ),
                ui.input_selectize(
                    "wavelet_wavelet", "Wavelet", choices={}, multiple=False
                ),
                ui.panel_conditional(
                    "input['wavelet_method'] == 'VisuShrink'",
                    ui.input_numeric(
                        "wavelet_sigma",
                        "Sigma reduction",
                        min=0,
                        max=10,
                        step=1,
                        value=2,
                    ),
                ),
                ui.input_slider(
                    "wavelet_levels", "Wavelet levels", min=1, max=10, value=5
                ),
            ),
            ui.div(
                {"style": "margin-bottom: 10px; width: 100%;"},
                ui.input_action_button(
                    "denoise",
                    "Denoise",
                    class_="btn-primary",
                    width="100%",
                ),
            ),
            ui.panel_conditional(
                "input['state'].includes('denoising_ended')",
                ui.download_button(
                    "download",
                    "Download",
                    filename="denoised_image.png",
                    data="denoised_img",
                    class_="btn-primary",
                    width="100%",
                ),
            ),
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
                if (event.value.includes('ready')) {
                    $('#denoise').prop('disabled', false);
                } else {
                    $('#denoise').prop('disabled', true);
                }
            }
        });
        """
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    img_path = reactive.Value(None)
    img_old_path = reactive.Value(None)
    img_original_path = reactive.Value(None)
    img_name = reactive.Value(None)
    img_new_name = reactive.Value(None)
    denosing_ended = reactive.Value(False)
    denoised_img = reactive.Value(None)
    ready = reactive.Value(False)

    @reactive.Effect
    @reactive.event(input.file)
    def file():
        if input.file() is not None:
            img_old_path.set(None)
            img_name.set(input.file()[0]["name"])
            path = input.file()[0]["datapath"]
            img_path.set(path)
            img_original_path.set(path)

            img_size = ip.ImageProperties.get_image_size(path)
            lesser = min(img_size)
            ui.update_slider("svd_k", max=lesser, value=lesser // 2)
            ui.update_numeric("svd_k_num", max=lesser, value=lesser // 2)

            ui.update_slider("fft_K", max=lesser, value=min(lesser, 10))
            ui.update_numeric("fft_K_num", max=lesser, value=min(lesser, 10))

    @reactive.Effect
    @reactive.event(input.denoise_method)
    def get_wavelets():
        if input.denoise_method() == "wavelet":
            wavelets = ip.ImageProperties.get_wavelets()
            ui.update_selectize("wavelet_wavelet", choices=wavelets)

    @reactive.Effect
    @reactive.event(input.svd_k)
    def update_svd_k_num():
        if input.svd_k() is not None:
            ui.update_numeric("svd_k_num", value=input.svd_k())

    @reactive.Effect
    @reactive.event(input.svd_k_num)
    def update_svd_k():
        if input.svd_k_num() is not None:
            ui.update_slider("svd_k", value=input.svd_k_num())

    @reactive.Effect
    @reactive.event(input.fft_K)
    def update_fft_K_num():
        if input.fft_K() is not None:
            ui.update_numeric("fft_K_num", value=input.fft_K())

    @reactive.Effect
    @reactive.event(input.fft_K_num)
    def update_fft_K():
        if input.fft_K_num() is not None:
            ui.update_slider("fft_K", value=input.fft_K_num())

    @reactive.Effect
    @output
    @render.image
    @reactive.event(img_path)
    def out_img():
        if input.file() is not None:
            denosing_ended.set(False)
            ready.set(True)
            img = ImgData(src=img_path.get(), alt="Image", height="100%", width="auto")
            return img

    @reactive.Effect
    @reactive.event(input.denoise)
    def denoise():
        if input.denoise_method() is not None and img_original_path.get() is not None:
            path = img_original_path.get()

            args = {
                "svd": {"k": input.svd_k()},
                "fft": {
                    "K": input.fft_K(),
                    "percentile": input.fft_percentile(),
                },
                "wavelet": {
                    "method": input.wavelet_method(),
                    "mode": input.wavelet_mode(),
                    "wavelet": input.wavelet_wavelet(),
                    "wavelet_levels": input.wavelet_levels(),
                    "sigma_reduction": input.wavelet_sigma(),
                },
            }
            mth = input.denoise_method()
            img = ip.ImageDenoising(path, mth)
            dimg = img.denoise(kwargs=args[mth])
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

            iio.imwrite(f"{base}.{ext}", denoised_img.get(), extension=f".{ext}")

            img_old_path.set(img_path.get())
            img_path.set(f"{base}.{ext}")

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
                yield output.getvalue()


app = App(app_ui, server)
