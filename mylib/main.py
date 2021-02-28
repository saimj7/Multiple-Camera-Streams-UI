
import _thread as thread
import mylib.func, time, cv2, sys, os
from mylib.settings import *
from datetime import datetime


class WorkCamera:

    def __init__(self, camera_list):
        self.camera_list = camera_list
        self.cap_list = []
        self.frame_list = []
        self.update_frame = []
        self.ret_image = []
        self.detect_rects_list = []
        self.detect_scores_list = []
        self.frame_ind_list = []
        # self.tracker_list = []
        self.count_list = []
        self.camera_list = camera_list
        self.camera_enable = []
        self.sql_table = ''

        for i in range(len(camera_list)):
            if camera_list[i] == '' or camera_list[i] is None:
                self.cap_list.append(None)
            else:
                self.cap_list.append(cv2.VideoCapture(camera_list[i]))

            # self.tracker_list.append(Tracker())
            self.frame_list.append(None)
            self.update_frame.append(False)
            self.ret_image.append(None)
            self.frame_ind_list.append(0)
            self.count_list.append(0)
            self.camera_enable.append(True)

        # create counting data save folder
        self.cur_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.save_folder = os.path.join(self.cur_path, SAVE_PATH)
        if not os.path.isdir(self.save_folder):
            os.mkdir(self.save_folder)

    def read_frame(self, camera_ind, scale_factor=1.0):
        while True:
            if self.cap_list[camera_ind] is None:
                self.frame_list[camera_ind] = None

            elif self.camera_enable[camera_ind]:
                ret, frame = self.cap_list[camera_ind].read()

                if ret:
                    if scale_factor != 1.0:
                        frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
                    self.frame_list[camera_ind] = frame
                    self.ret_image[camera_ind] = frame
                    self.update_frame[camera_ind] = True
                else:
                    cam_url = self.camera_list[camera_ind]
                    print("Fail to read camera!", cam_url)
                    self.cap_list[camera_ind].release()
                    time.sleep(0.5)
                    self.cap_list[camera_ind] = cv2.VideoCapture(cam_url)

            time.sleep(0.02)

    def check_valid_detection(self, rect_list, score_list, cam_ind):
        check_rect_list = []
        check_score_list = []

        for i in range(len(score_list)):
            if score_list[i] < DETECTION_THRESHOLD:
                continue

            # check ROI
            frame_height, frame_width = self.frame_list[cam_ind].shape[:2]
            roi_x1 = int(CAMERA_ROI[cam_ind][0] * frame_width)
            roi_x2 = int(CAMERA_ROI[cam_ind][2] * frame_width)
            roi_y1 = int(CAMERA_ROI[cam_ind][1] * frame_height)
            roi_y2 = int(CAMERA_ROI[cam_ind][3] * frame_height)
            if rect_list[i][0] < roi_x1 or rect_list[i][2] > roi_x2:
                continue
            elif rect_list[i][1] < roi_y1 or rect_list[i][3] > roi_y2:
                continue

            # check overlap with other rects
            f_overlap = False
            for j in range(len(check_rect_list)):
                if func.check_overlap_rect(check_rect_list[j], rect_list[i]):
                    if check_score_list[j] < score_list[i]:
                        check_score_list[j] = score_list[i]
                        check_rect_list[j] = rect_list[i]
                    f_overlap = True
                    break

            if f_overlap:
                continue

            # check width/height rate
            w = rect_list[i][2] - rect_list[i][0]
            h = rect_list[i][3] - rect_list[i][1]
            if max(w, h) / min(w, h) > 2:
                continue

            # register data
            check_rect_list.append(rect_list[i])
            check_score_list.append(score_list[i])

            # print(class_list[i], rect_list[i])

        return check_rect_list, check_score_list

    def draw_image(self, img, count, rects, scores, cam_ind):
        # draw ROI region
        frame_height, frame_width = img.shape[:2]
        roi_x1 = int(CAMERA_ROI[cam_ind][0] * frame_width)
        roi_x2 = int(CAMERA_ROI[cam_ind][2] * frame_width)
        roi_y1 = int(CAMERA_ROI[cam_ind][1] * frame_height)
        roi_y2 = int(CAMERA_ROI[cam_ind][3] * frame_height)
        cv2.rectangle(img, (roi_x1, roi_y1), (roi_x2, roi_y2), (100, 100, 100), 1)

        # draw objects with rectangle
        for i in range(len(rects)):
            rect = rects[i]
            cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (255, 0, 0), 2)
        return img

    def run_thread(self):
        # self.class_db.connect(host='78.188.225.187', database='camera', user='root', password='Aa3846sasa*-')
        self.sql_table = 'camera'

        for i in range(len(self.cap_list)):
            thread.start_new_thread(self.read_frame, (i, RESIZE_FACTOR))

        while True:
            for i in range(len(self.cap_list)):
                if self.frame_list[i] is not None:
                    img_org = self.draw_image(self.frame_list[i].copy(),
                                              count=0,
                                              rects=self.detect_rects_list[i],
                                              scores=self.detect_scores_list[i],
                                              cam_ind=i)
                    cv2.imshow('org' + str(i), img_org)

            key = cv2.waitKey(10)
            if key == ord('q'):
                break
            elif key == ord('s'):
                img_gray = cv2.cvtColor(self.frame_list[0], cv2.COLOR_BGR2GRAY)
                img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
                # img_color = img_color[20:-70, 180:-180]
                cv2.imwrite(str(time.time()) + '.jpg', img_color)

    def run(self):
        frame_ind = 0
        while True:
            frame_ind += 1
            ret, frame = self.cap_list[0].read()
            if not ret:
                break

            # resize image
            if RESIZE_FACTOR != 1.0:
                frame = cv2.resize(frame, None, fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)

            # detect
            valid_rects = []
            valid_scores = []
            img_ret = self.draw_image(frame,
                                      0, valid_rects, valid_scores, 0)

            cv2.imshow('ret', img_ret)
            if cv2.waitKey(10) == ord('q'):
                break


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cam_list = [sys.argv[1]]
    else:
        cam_list = CAMERA_URL

    class_work = WorkCamera(cam_list)

    if RUN_MODE_THREAD:
        class_work.run_thread()
    else:
        class_work.run()
