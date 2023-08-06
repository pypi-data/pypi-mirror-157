import sys
import os
import csv
import subprocess
import time
import argparse


# This function is to check whether all necessary csv and video files exist or not and return info array
def get_file_dir_exist_array(check_dir, file_name_array_input):
    file_dir_exist_array = []
    for name in file_name_array_input:
        file_exist = os.path.isfile(os.path.join(check_dir, name))
        file_dir_exist_array.append([name, file_exist])
    return file_dir_exist_array


# This function is to get the positions in given array
def get_position(search_input, array_in):
    idx_found = False
    return_idx = None
    for idx, val in enumerate(array_in):
        if val == search_input:
            idx_found = True
            return_idx = idx
            break

    if not idx_found:
        print(f"{search_input} can not be found!")

    return return_idx


# This function is to read given csv and return first data of given column
def get_timestamp_from_csv(csv_dir_input, column_name_input):
    with open(csv_dir_input, "r") as csv_file:
        csv_data_array = csv.reader(csv_file, delimiter=',')
        header_array = next(csv_data_array)
        first_row = next(csv_data_array)
        data_position = get_position(column_name_input, header_array)

        return float(first_row[data_position])


# This function is to get video length from given string
def get_video_length(string_input):
    start_marker = "duration="
    end_marker = "[/FORMAT]"
    start_index = string_input.find(start_marker)
    end_index = string_input.find(end_marker)

    return float(string_input[start_index + len(start_marker):end_index])


# This function is to change sec to ffmpeg input format string
def change_sec_to_ffmpeg_time_format(time_input):
    millisecond_string_raw = "%.3f" % (time_input % 1,)
    start_marker = "."
    start_index = millisecond_string_raw.find(start_marker)
    millisecond_string = millisecond_string_raw[start_index:len(millisecond_string_raw)]
    hour_min_second_format_string = time.strftime('%H:%M:%S', time.gmtime(time_input))

    return hour_min_second_format_string + millisecond_string


def main():
    parser = argparse.ArgumentParser(prog='pim_video',
                                     description='PIM_VIDEO package.')
    parser.add_argument('--version', action='version', version='1.0.0'),
    parser.add_argument("-d", dest="input_directory", required=True, default=sys.stdin,
                        help="directory folder to be processed", metavar="directory name")

    args = parser.parse_args()
    input_dir = args.input_directory

    # check whether input directory exists or not
    dir_exist = os.path.isdir(input_dir)
    if not dir_exist:
        print(f"Error! Input directory:{input_dir} does not exist.")
    else:
        print("Input directory is found.")
        file_name_array = ["gaze.csv", "left_eye_timestamp.csv",
                           "right_eye_timestamp.csv", "left_video.mp4", "right_video.mp4"]
        dir_exist_array = get_file_dir_exist_array(input_dir, file_name_array)
        all_file_found = True
        for exist_array in dir_exist_array:
            if not exist_array[1]:
                print(f"Error! {exist_array[0]} file is missing.")
                all_file_found = False
        if all_file_found:
            print("All necessary csv files and videos are found.")
            ffmpeg_check_cmd = "ffmpeg -version"
            ffmpeg_check_output = subprocess.check_output(ffmpeg_check_cmd)
            is_there_ffmpeg = "not found" not in ffmpeg_check_output.decode('utf-8')
            if is_there_ffmpeg:
                print("Essential software, ffmpeg is found and start processing...")
                os.chdir(input_dir)

                # rotate the videos
                left_v_rotate_cmd = "ffmpeg -i left_video.mp4 -vf \"transpose=2\" -b:v 10M -c:a copy " \
                                    "left_video_rotated.mp4 "
                right_v_rotate_cmd = "ffmpeg -i right_video.mp4 -vf \"transpose=2\" -b:v 10M -c:a copy " \
                                     "right_video_rotated.mp4 "
                os.system(left_v_rotate_cmd)
                os.system(right_v_rotate_cmd)
                print("Left and right videos have been rotated.")

                # read left and right timestamps
                left_csv_dir = os.path.join(input_dir, "left_eye_timestamp.csv")
                left_timestamp = get_timestamp_from_csv(left_csv_dir, "left_eye_timestamp")
                print(f"Left timestamp: {left_timestamp}")
                right_csv_dir = os.path.join(input_dir, "right_eye_timestamp.csv")
                right_timestamp = get_timestamp_from_csv(right_csv_dir, "right_eye_timestamp")
                print(f"Right timestamp: {right_timestamp}")
                timestamp_diff = round(left_timestamp - right_timestamp
                                       if left_timestamp >= right_timestamp
                                       else right_timestamp - left_timestamp, 3)
                print(f"Timestamp difference: {timestamp_diff}")
                timestamp_diff_ffmpeg_format = change_sec_to_ffmpeg_time_format(timestamp_diff)

                # check the length of both rotated videos
                left_v_len_check_cmd = "ffprobe -i left_video_rotated.mp4 -v quiet -show_entries format=duration " \
                                       "-hide_banner "
                right_v_len_check_cmd = "ffprobe -i right_video_rotated.mp4 -v quiet -show_entries format=duration " \
                                        "-hide_banner "
                left_v_len_check_output = subprocess.check_output(left_v_len_check_cmd).decode('utf-8')
                left_v_length = get_video_length(left_v_len_check_output)
                print(f"Left video length in sec: {left_v_length}")
                right_v_len_check_output = subprocess.check_output(right_v_len_check_cmd).decode('utf-8')
                right_v_length = get_video_length(right_v_len_check_output)
                print(f"Right video length in sec: {right_v_length}")

                # trimming the side which has earlier timestamp
                trim_type = None
                if left_timestamp >= right_timestamp:
                    right_available_length = right_v_length - timestamp_diff
                    right_available_length_ffmpeg_format = change_sec_to_ffmpeg_time_format(right_available_length)
                    trim_type = "right"
                    right_v_trim_cmd = f"ffmpeg -i right_video_rotated.mp4 " \
                                       f"-ss {timestamp_diff_ffmpeg_format} " \
                                       f"-t {right_available_length_ffmpeg_format} " \
                                       f"-b:v 10M -c:a copy right_video_trimmed.mp4"
                    os.system(right_v_trim_cmd)
                    print("Right video is trimmed.")
                else:
                    left_available_length = left_v_length - timestamp_diff
                    left_available_length_ffmpeg_format = change_sec_to_ffmpeg_time_format(left_available_length)
                    trim_type = "left"
                    left_v_trim_cmd = f"ffmpeg -i left_video_rotated.mp4 " \
                                      f"-ss {timestamp_diff_ffmpeg_format} " \
                                      f"-t {left_available_length_ffmpeg_format} " \
                                      f"-b:v 10M -c:a copy left_video_trimmed.mp4"
                    os.system(left_v_trim_cmd)
                    print("Left video is trimmed.")

                # merge videos
                right_trim_merge_cmd = "ffmpeg -i left_video_rotated.mp4 -i right_video_trimmed.mp4 -filter_complex " \
                                       "hstack=inputs=2:shortest=1 -b:v 10M -c:a copy left_right_combined.mp4 "
                left_trim_merge_cmd = "ffmpeg -i left_video_trimmed.mp4 -i right_video_rotated.mp4 -filter_complex " \
                                      "hstack=inputs=2:shortest=1 -b:v 10M -c:a copy left_right_combined.mp4 "
                if trim_type == "right":
                    os.system(right_trim_merge_cmd)
                    print("Left and right videos are merged into left_right_combined.mp4")
                elif trim_type == "left":
                    os.system(left_trim_merge_cmd)
                    print("Left and right videos are merged into left_right_combined.mp4")
                else:
                    print(f"Error! Trimming type is {trim_type}.")
                    pass

            else:
                print("Essential software, ffmpeg is not found.")
                print("Please read how to install ffmpeg from links below.")
                print("For windows: https://www.wikihow.com/Install-FFmpeg-on-Windows")
                print("For mac: https://bbc.github.io/bbcat-orchestration-docs/installation-mac-manual/")
