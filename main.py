import itertools
import cv2
from tqdm import tqdm
from VideoLoader import VideoLoader

height_resolution = 100  # Lower resolution gives faster results, but might not count every loading frame if the video is highly compressed
check_each = 2  # Check 1 out of x frames assuming the inaccuracies will cancel out on long runs (2 still gives max precision for 60fps videos since the game runs at 30fps)
download_quality = {"resolution": "360p", "fps": 30}


selection_text = lambda element: f"Select the {element} then press enter"


def select_object(video: VideoLoader, searching: str) -> tuple[int, ...]:
    pouch_frame = int(input(f"Frame where you can see the {searching}: "))
    for i, frame in enumerate(video):
        if i != pouch_frame:
            continue

        cv2.namedWindow(selection_text(searching), 2)
        roi_480p = cv2.selectROI(selection_text(searching), cv2.resize(frame, (int(len(frame[0]) * 480 / len(frame)), 480)))
        roi = tuple(int(i * height_resolution / 480) for i in roi_480p)

        cv2.destroyWindow(selection_text(searching))
        return roi


def roi_is_black(frame, roi: tuple[int, ...], resize_ratio: float, area: int) -> bool:
    cropped_frame = cv2.resize(frame, (int(len(frame[0]) / resize_ratio), height_resolution))[
                    roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
    black_pixels = 0
    for pixel in itertools.chain.from_iterable(cropped_frame):
        if sum(pixel) // 3 < 10:
            black_pixels += 1
    if black_pixels / area >= 0.95:
        return True


def count_loading_frames(video: VideoLoader):
    first_frame = int(input("Frame right before the run starts: "))
    resize_ratio = video.raw_data.get(cv2.CAP_PROP_FRAME_HEIGHT) / height_resolution

    roi_pouch = select_object(video, "pouch")
    area_pouch = roi_pouch[2] * roi_pouch[3]

    loading_frame_indexes = []
    for i, frame in tqdm(enumerate(video), "Analyzing frame", unit="", colour="#ffffff", total=len(video)):
        if i <= first_frame or i % check_each != 0:
            continue

        if roi_is_black(frame, roi_pouch, resize_ratio, area_pouch):
            loading_frame_indexes.append(i)

    print(f"Probably a loading screen: {loading_frame_indexes[0] + int(32 * 30 / video.framerate)}")
    roi_moon = select_object(video, "loading moon")
    area_moon = roi_moon[2] * roi_moon[3]

    loading_frames = 0
    for loading_frame_index in tqdm(loading_frame_indexes, "Checking again", unit="", colour="#ffffff", total=len(loading_frame_indexes)):
        loading_frame = video[loading_frame_index]

        if not roi_is_black(loading_frame, roi_moon, resize_ratio, area_moon):
            loading_frames += check_each

    return loading_frames


time_info = [("h", 60 * 60), ("m", 60), ("s", 1), ("ms", 0.001)]


def seconds_to_string(seconds):
    res = ""
    for unit, in_seconds in time_info:
        unit_value = int(seconds / in_seconds)
        res += f"{unit_value}{unit} "
        seconds -= unit_value * in_seconds
    return res


def main():
    recorded_time = float(input("Recorded time: "))

    video = VideoLoader(input("Enter a youtube/speedrun.com link or a path to a video file: "))
    seconds_of_loading = count_loading_frames(video) / video.framerate

    print(seconds_to_string(seconds_of_loading), seconds_to_string(recorded_time - seconds_of_loading))


if __name__ == "__main__":
    main()
