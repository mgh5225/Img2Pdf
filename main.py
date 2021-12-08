from PIL import Image
import reader
import writer
import argparse
import concurrent.futures
from threading import Lock
import glob


def usage():
    guide = 'python3 main.py -i <file_name> -o <file_name> -a <alpha> -b <beta> -mf <max_frames> -mw <max_workers> -mr <max_readers>'
    return guide


def arguments():
    parse = argparse.ArgumentParser(usage=usage())
    parse.add_argument(
        '-i', dest='file', help='Input File Name e.g. video.mp4 or Directory e.g. ~/videos/*.mp4', type=str, required=True)
    parse.add_argument(
        '-o', dest='pdf', help='Output File Name e.g. slides.pdf', type=str, required=True)
    parse.add_argument(
        '-a', dest='alpha', help='Alpha e.g. 5', type=float, default=5)
    parse.add_argument(
        '-b', dest='beta', help='Beta e.g. 0', type=float, default=0)
    parse.add_argument(
        '-mf', dest='max_frames', help='Max Frames e.g. 600', type=int, default=600)
    parse.add_argument(
        '-mw', dest='max_workers', help='Max Workers e.g. 5', type=int, default=3)
    parse.add_argument(
        '-mr', dest='max_readers', help='Max Readers e.g. 5', type=int, default=3)
    return parse.parse_args()


if __name__ == "__main__":
    args = arguments()
    fileNames = glob.glob(args.file)
    pdfName = args.pdf
    alpha = args.alpha
    beta = args.beta
    max_frames = args.max_frames
    max_workers = args.max_workers
    max_readers = args.max_readers

    images = []
    writers_frames = []

    frame_lock = Lock()

    for fileName in fileNames:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as reader_executor:
            new_reader = reader.Reader(fileName)
            frames = []
            writers = []
            read_future = reader_executor.submit(new_reader.read)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as writer_executor:
                for (ret, frame) in read_future.result():
                    if ret == True:
                        frames.append(frame)
                        if len(frames) == max_frames:
                            new_writer = writer.Writer(frames, alpha)
                            writers.append(
                                writer_executor.submit(new_writer.run))
                            print("Writer " +
                                  str(writer.Writer.writers_number) + " Added")
                            if beta > 0:
                                frames = frames[-beta:]
                            else:
                                frames = []

                    else:
                        break
                for f_writer in concurrent.futures.as_completed(writers):
                    frame_lock.acquire()
                    writers_frames += f_writer.result()
                    frame_lock.release()

    writer.Writer.writers_number = 0
    final_writer = writer.Writer(writers_frames, alpha)

    for frame in final_writer.run(True):
        images.append(Image.fromarray(frame))

    images[0].save(pdfName, save_all=True, append_images=images[1:])
