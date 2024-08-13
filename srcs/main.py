from algo.save_video_as_midi import save_video_as_midi
from ui.main_app import App
from p2m import p2m_path


def main():
    # save_video_as_midi(p2m_path.data)
    App().mainloop()


if __name__ == '__main__':
    main()
