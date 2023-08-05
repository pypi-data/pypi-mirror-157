def cut_video(video_path,init,end,path2save):
    """ Function to cut videos using ffmpeg

    Parameters
    ----------

    video_path : str
        The video location in drive or HDD
    int: hour (HH:MM:SS)
        The start point to cut 
    end: hour (HH:MM:SS)
        The cut end point
    path2save: str
        The path to save the video. Here you must
        determine the video name and the desired
        extension.

    Example
    ----------

    path = '/content/video1'
    init = 00:00:01,
    end  = 00:58:00,
    save = '/content/drive/MyDrive/video_cuted.mp4'

    cut_video(path,init,end,save)

    See Also
    --------

    Developed by Tulio Almeida.
    https://github.com/tuliofalmeida/scroll-of-seals
        """
    from subprocess import call
    call(['ffmpeg', '-i', video_path, '-ss', init,'-to',end,'-c:v','copy','-c:a', 'copy', path2save])