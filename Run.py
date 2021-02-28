from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
import numpy as np
import time, cv2
import _thread as thread
from mylib import func
from mylib.settings import *
from mylib.main import WorkCamera



class BestApp(App):

    screen_names = ListProperty([])
    screens = {}  # Dict of all screens

    title = StringProperty()
    camera_list = ListProperty()
    txt_db_host = StringProperty()
    txt_db_user = StringProperty()
    txt_db_password = StringProperty()
    txt_db_port = StringProperty()
    txt_db_database = StringProperty()
    txt_db_table = StringProperty()

    def __init__(self, **kwargs):
        self.setting = func.read_json(CONFIG_FILE)

        self.camera_list = self.setting['camera_url']
        self.view_mode = -1
        self.image_no_camera = cv2.imread('logo/1.jpg')
        self.image_no_camera_small = cv2.resize(self.image_no_camera, (PIECE_WIDTH, PIECE_HEIGHT))

        self.txt_db_host = self.setting['db_host']
        self.txt_db_port = self.setting['db_port']
        self.txt_db_user = self.setting['db_user']
        self.txt_db_password = self.setting['db_password']
        self.txt_db_database = self.setting['db_database']
        self.txt_db_table = self.setting['db_table']

        self.class_main = WorkCamera(self.camera_list)

        for i in range(len(self.class_main.cap_list)):
            thread.start_new_thread(self.class_main.read_frame, (i, RESIZE_FACTOR))

        self.title = 'Camera View'
        Window.size = (1200, 800)
        Window.left = 100
        Window.top = 50

        self.event_take_video = None
        self.fps = 30
        self.on_resume()
        super(BestApp, self).__init__(**kwargs)

    # --------------------------- Main Menu Event -----------------------------
    def go_setting(self):
        self.title = 'Setting'
        self.go_screen('dlg_setting', 'left')

    def on_exit(self):
        exit(0)

    # ---------------------- Camera Setting dialog Event ------------------------
    def on_sel_view_mode(self, mode):
        self.view_mode = mode

    def on_cam_set(self, cam1, cam2, cam3, cam4, cam5, cam6, cam7, cam8, host, port, user, password, database, table):
        cam_list = [cam1, cam2, cam3, cam4, cam5, cam6, cam7, cam8]
        f_change_camera = False
        for i in range(len(cam_list)):
            if self.camera_list[i] != cam_list[i]:
                f_change_camera = True
                self.class_main.camera_enable[i] = False
                time.sleep(0.5)
                self.class_main.camera_list[i] = cam_list[i]
                if self.class_main.cap_list[i] is not None:
                    self.class_main.cap_list[i].release()
                self.class_main.cap_list[i] = cv2.VideoCapture(cam_list[i])
                self.class_main.tracker_list[i].format()
                self.class_main.camera_enable[i] = True

        if f_change_camera:
            self.camera_list = cam_list

        f_change_db = False
        if self.txt_db_host != host or self.txt_db_table != table or self.txt_db_database != database or \
                self.txt_db_user != user or self.txt_db_password != password or self.txt_db_port != port:
            f_change_db = True

        if f_change_db:
            self.txt_db_host = host
            self.txt_db_port = port
            self.txt_db_user = user
            self.txt_db_password = password
            self.txt_db_database = database
            self.txt_db_table = table

            self.class_main.sql_table = table

        # save config file
        if f_change_camera or f_change_db:
            print("Updated config file!")
            self.setting['camera_url'] = cam_list
            self.setting["db_host"] = host
            self.setting["db_user"] = user
            self.setting["db_port"] = port
            self.setting["db_password"] = password
            self.setting["db_database"] = database
            self.setting["db_table"] = table
            func.write_json(CONFIG_FILE, self.setting)

        self.title = 'Camera View'
        self.go_screen('dlg_menu', 'right')

        self.on_resume()

    def on_reset(self):
        for i in range(len(self.class_main.tracker_list)):
            self.class_main.tracker_list[i].format()

        print("Reset Counting data!")

    def on_return(self):
        self.title = 'Camera View'
        self.go_screen('dlg_menu', 'right')

    # ------------------------ Image Processing -------------------------------
    def on_stop(self):
        if self.event_take_video is not None and self.event_take_video.is_triggered:
            self.event_take_video.cancel()

    def on_resume(self):
        if self.event_take_video is None:
            self.event_take_video = Clock.schedule_interval(self.get_frame, 1.0 / self.fps)
        elif not self.event_take_video.is_triggered:
            self.event_take_video()

    def get_frame(self, *args):

        def get_piece_img(ind):
            if ind >= len(self.class_main.ret_image) or self.class_main.ret_image[ind] is None:
                return self.image_no_camera_small
            else:
                return cv2.resize(self.class_main.ret_image[ind], (PIECE_WIDTH, PIECE_HEIGHT))

        if self.view_mode == -1:    # all camera
            # merge images
            img1 = np.concatenate((get_piece_img(0), get_piece_img(1)), axis=1)
            img2 = np.concatenate((img1, get_piece_img(2)), axis=1)
            img3 = np.concatenate((get_piece_img(3), get_piece_img(4)), axis=1)
            img4 = np.concatenate((img3, get_piece_img(5)), axis=1)
            img5 = np.concatenate((get_piece_img(6), get_piece_img(7)), axis=1)
            img6 = np.concatenate((img5, get_piece_img(8)), axis=1)
            img7 = np.concatenate((img2, img4), axis=0)
            frame = np.concatenate((img7, img6), axis=0)
            # draw grid
            cv2.line(frame, (PIECE_WIDTH, 0), (PIECE_WIDTH, PIECE_HEIGHT * 3), (0, 0, 0), 1)
            cv2.line(frame, (PIECE_WIDTH * 2, 0), (PIECE_WIDTH * 2, PIECE_HEIGHT * 3), (0, 0, 0), 1)
            cv2.line(frame, (0, PIECE_HEIGHT), (PIECE_WIDTH * 3, PIECE_HEIGHT), (0, 0, 0), 1)
            cv2.line(frame, (0, PIECE_HEIGHT * 2), (PIECE_WIDTH * 3, PIECE_HEIGHT * 2), (0, 0, 0), 1)
        else:
            if self.class_main.ret_image[self.view_mode] is None:
                frame = self.image_no_camera
            else:
                frame = self.class_main.ret_image[self.view_mode]

        self.frame_to_buf(frame=frame)

    def frame_to_buf(self, frame):
        fh, fw = frame.shape[:2]
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        self.root.ids.img_video.texture = Texture.create(size=(fw, fh))
        self.root.ids.img_video.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

    def build(self):
        self.load_screen()
        self.go_screen('dlg_menu', 'right')

    def go_screen(self, dest_screen, direction):
        sm = self.root.ids.sm
        sm.switch_to(self.screens[dest_screen], direction=direction)

    def load_screen(self):
        self.screen_names = ['dlg_menu', 'dlg_setting']
        for i in range(len(self.screen_names)):
            screen = Builder.load_file('kv_dlg/' + self.screen_names[i] + '.kv')
            self.screens[self.screen_names[i]] = screen
        return True


if __name__ == '__main__':
    Config.set('graphics', 'resizable', 0)
    BestApp().run()
