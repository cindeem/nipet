
#. Handle Missing frames
#. get rid of comments in data columns
#. calc midtimes from frame slices
    pibtimes = ft.FrameTime().from_csv(infile, units='sec')
    midtimes = pibtimes.get_midtimes()
#. Add check for swapped duration and stoptime columns
    return in correct order
#. Add tests for weird pibtimes issues
#. GEnerate an example csv with notes etc to handle these odd cases

Specification of how a frametime file should look.

First column: frame numbers. 
    * Frame numbers should be integers, 
    * No special characters (e.g. \*, #)
    * If a frame gets split, treat it as multiple separate frames, and
      make note of it in the notes column.
    * If a frame is missing, keep the frame number, but leave the other 
      columns blank. Check how conversion handles missing frames.



