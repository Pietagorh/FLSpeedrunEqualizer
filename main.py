import itertools
import cv2
from tqdm import tqdm
from VideoLoader import VideoLoader


height_resolution = 480  # Lower resolution gives faster results, but might not count every loading frame if the video is highly compressed
check_each = 2  # Check 1 out of x frames assuming the inaccuracies will cancel out on long runs (2 still gives max precision for 60fps videos since the game runs at 30fps)

pouch_selection_text = "Select the pouch then press enter"


def populate_variables(video: VideoLoader):
    pouch_frame = int(input("Frame where you can see the pouch: "))
    for i, frame in tqdm(enumerate(video), "Searching first frame", leave=False):
        if i != pouch_frame:
            continue

        cv2.namedWindow(pouch_selection_text, 2)
        roi_480p = cv2.selectROI(pouch_selection_text, cv2.resize(frame, (int(len(frame[0]) * 480 / len(frame)), 480)))
        roi = tuple(int(i * height_resolution / 480) for i in roi_480p)

        cv2.destroyWindow(pouch_selection_text)

        resize_ratio = len(frame) / height_resolution
        return resize_ratio, roi


def count_loading_frames(video: VideoLoader):
    first_frame = int(input("Frame right before the run starts: "))

    resize_ratio, roi = populate_variables(video)
    area = roi[2] * roi[3]

    loading_frames = 0
    for i, frame in tqdm(enumerate(video), "Analyzing frame", unit="", colour="#ffffff", total=len(video)):
        if i <= first_frame or i % 2 != 0:
            continue

        cropped_frame = cv2.resize(frame, (int(len(frame[0]) / resize_ratio), height_resolution))[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
        black_pixels = 0
        for pixel in itertools.chain.from_iterable(cropped_frame):
            if sum(pixel) // 3 < 10:
                black_pixels += 1
        if black_pixels / area >= 0.9:
            loading_frames += 2
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
    video = VideoLoader(input("Enter a youtube/speedrun.com link or a path to a video file: "))
    seconds_of_loading = count_loading_frames(video) / video.framerate

    print(seconds_to_string(seconds_of_loading))


if __name__ == "__main__":
    main()
