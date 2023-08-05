# from ROI_analysis_3 import ROIAnalyzer
# from simba.drop_bp_cords import get_fn_ext, createColorListofList
# from simba.features_scripts.unit_tests import read_video_info
# import pandas as pd
# import os
# import itertools
# import cv2
# from simba.misc_tools import get_video_meta_data
# from collections import defaultdict
#
# class ROIPlot(object):
#     def __init__(
#             self,
#             ini_path=None,
#             video_path=None):
#
#
#         self.roi_analyzer = ROIAnalyzer(ini_path=ini_path, data_path='outlier_corrected_movement_location')
#         self.roi_analyzer.read_roi_dfs()
#         self.video_path = video_path
#         _, self.video_name, _ = get_fn_ext(video_path)
#         self.roi_analyzer.files_found = [os.path.join(self.roi_analyzer.input_folder, self.video_name + '.' + self.roi_analyzer.file_type)]
#         if not os.path.isfile(self.roi_analyzer.files_found[0]):
#             raise FileNotFoundError(print('Could not find the file at path {}. Please make sure you have corrected body-part outliers or indicated that you want to skip outlier correction'.format(self.roi_analyzer.files_found[0])))
#         self.roi_analyzer.analyze_ROIs()
#         self.roi_entries_df = pd.concat(self.roi_analyzer.entry_exit_df_lst, axis = 0)
#         self.data_df = self.roi_analyzer.data_df
#         self.video_shapes = list(itertools.chain(self.roi_analyzer.video_recs['Name'].unique(), self.roi_analyzer.video_circs['Name'].unique(),self.roi_analyzer.video_polys['Name'].unique()))
#         self.shape_columns = []
#         for animal in self.roi_analyzer.multiAnimalIDList:
#             for shape_name in self.video_shapes:
#                 self.data_df[animal + '_' + shape_name] = 0
#                 self.shape_columns.append(animal + '_' + shape_name)
#         self.bp_dict = self.roi_analyzer.bp_dict
#
#         self.output_folder = os.path.join(self.roi_analyzer.project_path, 'frames', 'output', 'ROI_analysis')
#         if not os.path.exists(self.output_folder):
#             os.makedirs(self.output_folder)
#
#     def insert_data(self):
#         self.roi_entries_dict =self.roi_entries_df[['Animal', 'Shape', 'Entry_times', 'Exit_times']].to_dict(orient='records')
#         for entry_dict in self.roi_entries_dict:
#             entry_dict['frame_range'] = list(range(entry_dict['Entry_times'], entry_dict['Exit_times'] + 1))
#             col_name = entry_dict['Animal'] + '_' + entry_dict['Shape']
#             self.data_df[col_name][self.data_df.index.isin(entry_dict['frame_range'])] = 1
#
#     def calc_text_locs(self):
#         add_spacer = 2
#         self.loc_dict = {}
#         for animal_cnt, animal_name in enumerate(self.roi_analyzer.multiAnimalIDList):
#             self.loc_dict[animal_name] = {}
#             for shape in self.video_shapes:
#                 self.loc_dict[animal_name][shape] = {}
#                 self.loc_dict[animal_name][shape]['timer_text'] = '{} {} {}'.format(shape, animal_name, 'timer:')
#                 self.loc_dict[animal_name][shape]['entries_text'] = '{} {} {}'.format(shape, animal_name, 'entries:')
#                 self.loc_dict[animal_name][shape]['timer_text_loc'] = ((self.video_meta_data['width'] + 5), (self.video_meta_data['height'] - (self.video_meta_data['height'] + 10) + self.space_scale * add_spacer))
#                 self.loc_dict[animal_name][shape]['timer_data_loc'] = (int(self.video_meta_data['width']-(self.video_meta_data['width']/8)), (self.video_meta_data['height'] - (self.video_meta_data['height'] + 10) + self.space_scale*add_spacer))
#                 add_spacer += 1
#                 self.loc_dict[animal_name][shape]['entries_text_loc'] = ((self.video_meta_data['width'] + 5), (self.video_meta_data['height'] - (self.video_meta_data['height'] + 10) + self.space_scale * add_spacer))
#                 self.loc_dict[animal_name][shape]['entries_data_loc'] = (int(self.video_meta_data['width'] - (self.video_meta_data['width'] / 8)), (self.video_meta_data['height'] - (self.video_meta_data['height'] + 10) + self.space_scale * add_spacer))
#                 add_spacer += 1
#
#     def visualize_ROI_data(self):
#         save_path = os.path.join(self.output_folder, self.video_name + '.avi')
#         self.cap = cv2.VideoCapture(self.video_path)
#         self.video_meta_data = get_video_meta_data(self.video_path)
#         video_settings, pix_per_mm, fps = read_video_info(self.roi_analyzer.vid_info_df, self.video_name)
#         self.space_scale, radius_scale, res_scale, font_scale = 25, 10, 1500, 0.8
#         max_dim = max(self.video_meta_data['width'], self.video_meta_data['height'])
#         font = cv2.FONT_HERSHEY_TRIPLEX
#         draw_scale, font_size = int(radius_scale / (res_scale / max_dim)), float(font_scale / (res_scale / max_dim))
#         fourcc = cv2.VideoWriter_fourcc(*'XVID')
#         spacing_scaler = int(self.space_scale / (res_scale / max_dim))
#         writer = cv2.VideoWriter(save_path, fourcc, fps, (self.video_meta_data['width'] * 2, self.video_meta_data['height']))
#         color_lst = createColorListofList(self.roi_analyzer.no_animals, int((len(self.roi_analyzer.bp_columns) / 3)))[0]
#
#         self.calc_text_locs()
#
#         frame_cnt = 0
#         while (self.cap.isOpened()):
#             try:
#                 ret, img = self.cap.read()
#                 if ret:
#                     add_spacer = 2
#                     border_img = cv2.copyMakeBorder(img, 0, 0, 0, int(self.video_meta_data['width']), borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])
#                     for animal_cnt, animal_name in enumerate(self.roi_analyzer.multiAnimalIDList):
#                         bp_data = self.data_df.loc[frame_cnt, self.bp_dict[animal_name]].values
#                         if self.roi_analyzer.p_thresh > bp_data[2]:
#                             cv2.circle(border_img, (int(bp_data[0]), int(bp_data[1])), draw_scale, color_lst[animal_cnt], -1)
#                             cv2.putText(border_img, animal_name, (int(bp_data[0]), int(bp_data[1])), font, font_size, color_lst[animal_cnt], 1)
#
#                         for _, row in self.roi_analyzer.video_recs.iterrows():
#                             top_left_x, top_left_y, shape_name = row['topLeftX'], row['topLeftY'], row['Name']
#                             bottom_right_x, bottom_right_y = row['Bottom_right_X'], row['Bottom_right_Y']
#                             thickness, color = row['Thickness'], row['Color BGR']
#                             cv2.rectangle(border_img, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), color, thickness)
#                             cv2.putText(border_img, self.loc_dict[animal_name][shape_name]['timer_text'], self.loc_dict[animal_name][shape_name]['timer_text_loc'], font, font_size, color, 1)
#                             cv2.putText(border_img, self.loc_dict[animal_name][shape_name]['entries_text'],self.loc_dict[animal_name][shape_name]['entries_text_loc'], font, font_size, color, 1)
#
#
#
#         #
#         #
#         #             for _, row in self.roi_analyzer.video_circs.iterrows():
#         #                 center_x, center_y, radius, shape_name = row['centerX'], row['centerY'], row['radius'], row['Name']
#         #
#         #             #
#         #             # for _, row in self.roi_analyzer.video_polys.iterrows():
#         #
#         #
#         #
#         #
#         #
#         #             self.video_recs = self.rectangles_df.loc[self.rectangles_df['Video'] == video_name]
#         #             self.video_circs = self.circles_df.loc[self.circles_df['Video'] == video_name]
#         #             self.video_polys = self.polygon_df.loc[self.polygon_df['Video'] == video_name]
#         #
#         #
#         #
#         #                 #for shape_name in self.video_shapes:
#         #
#         #
#         #
#         #
#         #
#         #
#             except Exception as e:
#                 writer.release()
#                 print(e.args)
#                 print(
#                     'NOTE: index error / keyerror. Some frames of the video may be missing. Make sure you are running latest version of SimBA with pip install simba-uw-tf-dev')
#                 break
#         #
#         #
#         #
#         #
#
#
#
# test = ROIPlot(ini_path=r"Z:\DeepLabCut\DLC_extract\Troubleshooting\ROI_2_animals\project_folder\project_config.ini", video_path=r"Z:\DeepLabCut\DLC_extract\Troubleshooting\ROI_2_animals\project_folder\videos\Video7.mp4")
# test.insert_data()
# test.visualize_ROI_data()
#
#     #
#     #
#     #
#     # def __init__(self,
#     #              ini_path=None,
#     #              video_path=None):
#     #
#     #     config = ConfigParser()
#     #     config.read(ini_path)
#     #     self.project_path = config.get('General settings', 'project_path')
#     #
#     #     try:
#     #         self.no_animals = config.getint('ROI settings', 'no_of_animals')
#     #     except NoOptionError:
#     #         self.no_animals = config.getint('General settings', 'animal_no')
#     #
#     #     try:
#     #         self.file_type = config.get('General settings', 'workflow_file_type')
#     #     except NoOptionError:
#     #         self.file_type = 'csv'
#     #     try:
#     #         self.p_thresh = config.getfloat('ROI settings', 'probability_threshold')
#     #     except NoOptionError:
#     #         self.p_thresh = 0.000
#     #
#     #     self.multiAnimalStatus, self.multiAnimalIDList = check_multi_animal_status(config, self.no_animals)
#     #     self.bp_dict = defaultdict(list)
#     #     self.bp_columns = []
#     #     for cnt, animal in enumerate(self.multiAnimalIDList):
#     #         bp_name = config.get('ROI settings', 'animal_' + str(cnt + 1) + '_bp')
#     #         for c in ['_x', '_y', '_p']:
#     #             self.bp_dict[animal].append(bp_name + c)
#     #             self.bp_columns.append(bp_name + c)
#     #
#     #
