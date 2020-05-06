import audioread
import boto3
import io
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import requests
import time
import uuid
print("Im HERE AT THE generate report images")
s3 = boto3.client('s3')
print("S3")
print(s3)
def send_callback(context, payload):
    print("inside send_callback")
    start = time.time()
    print("time")
    print(start)
    requests.post(context['callback_url'], json=payload)
    elapsed = time.time() - start
    print("DONE")
    print('Elapsed time for sending callback: {:.3f} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, context['report_uid'], context['user_story_uid'], context['request_id']))
    
def map_to_pixels(length, pixel_length, words_length, offset):
    unit = pixel_length/length
    pixel_coordinates = []
    previous_words_length = 0
    for word_length in words_length:
        pixel_coordinates.append(int(((word_length/2)+previous_words_length)*unit + offset))
        previous_words_length = previous_words_length + word_length + 1
    return pixel_coordinates

def calculate_heights(line):
    heights = []
    for element in line:
        point1 = int(element[0])
        point2 = int(element[1])
        height = point2 - point1
        heights.append(height)
        normalized_heights = [height/max(heights) for height in heights]  
    return normalized_heights

def generate_audio_line(start_end_times, normalized_start, textSize):
    stress_line = []
    for start_end_time in start_end_times:
        stress_line.append((start_end_time[0]-normalized_start[0], start_end_time[1]-normalized_start[1]))

    maximum = stress_line[-1][1]

    normalized_stress_line = []
    for line in stress_line:
        normalized_stress_line.append((line[0]*textSize[0]/maximum, line[1]*textSize[0]/maximum))

    audio_line = tuple(normalized_stress_line)
    normalized_heights = calculate_heights(audio_line)
    heights = [int(height*210) for height in normalized_heights]

    return audio_line, heights

# this is where we use the Gentle forced aligner to get information
def run_gentle_forced_aligner(context, audio_filename, transcript_filename):
    start = time.time()

    output_filename = '/report_images/' + os.path.splitext(os.path.basename(audio_filename))[0] + '.json'
    cmd = 'python /gentle/align.py {} {} -o {}'.format(audio_filename, transcript_filename, output_filename)
    os.system(cmd)

    elapsed = time.time() - start
    print('Elapsed time for Gentle forced aligner: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    
    phonemes = {}
    with open(output_filename) as f:
        phonemes = json.load(f)
    
    return phonemes

# parse the audio using Gentle forced aligner and get the time stamps for the renders
def parse_audio(context, audio_filename, audio_system_filename, transcript, transcript_filename): 
    start = time.time()

    phonemes = run_gentle_forced_aligner(context, audio_system_filename, transcript_filename)

    phoneme_words = phonemes['words']

    ## this cuts the audio in to the words we are analysing
    loadAudioStart = time.time()

    sampling_rate = 0
    with audioread.audio_open(audio_system_filename) as f:
        sampling_rate =  f.samplerate

    elapsed = time.time() - loadAudioStart
    print('Elapsed time for loading audio file: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    
    words = {}
    start_end_times = []
    index = 0
    for word in phoneme_words:
        index += 1
        start_end_times.append((int(word['start']*sampling_rate), int(word['end']*sampling_rate )))

    elapsed = time.time() - start
    print('Elapsed time for parse audio: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    
    return start_end_times

def generate_stress_image(context, master_audio_heights, user_audio_heights, transcript, textSize, font, user_audio_filename):
    start = time.time()
    length_text = len(transcript)
    length_words = [len(word) for word in transcript.split()]

    # Create a black image
    img = Image.new('RGB', (1000, 450), color = (20, 20, 20))
    d = ImageDraw.Draw(img)
    textSize = d.textsize(transcript, font=font)

    img = Image.new('RGB', (textSize[0]+20 , 450), color = (20, 20, 20))
    d = ImageDraw.Draw(img)
    d.text((10, 400), transcript, fill='white', font=font)
    d.text((40, 100), "Sentence Stress", fill='white', font=font)
    
    sentence = map_to_pixels(length_text, textSize[0], length_words, 20)

    master_heights = []
    for index, height in enumerate(master_audio_heights):
        master_heights.append(height)
        d.line([(sentence[index], 400), (sentence[index], 400 - height)], fill=(255, 255, 255), width=10)

    user_heights = []
    for index, height in enumerate(user_audio_heights):
        user_heights.append(height)
        d.line([(sentence[index], 400), (sentence[index], 400 - height)], fill=(76, 217, 100), width=5)

    buf = io.BytesIO()
    img.save(buf, format='JPEG')

    scores = []
    for i in range(len(master_heights)):
        scores.append(abs(master_heights[i] - user_heights[i]))

    elapsed = time.time() - start
    print('Elapsed time for generating stress image: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, user_audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    return buf.getvalue(), (1 - (sum(scores)/len(scores))/210)*100

def generate_rhythm_image(context, master_audio_line, user_audio_line, transcript, textSize, font, user_audio_filename):
    start = time.time()
    # Create a black image
    img = Image.new('RGB', (textSize[0]+20, 310), color = (20, 20, 20))
    d = ImageDraw.Draw(img)

    for element in master_audio_line:
        point1 = int(element[0])
        point2 = int(element[1])
        d.line([(point1 + 20, 170), (point2, 170)], fill=(255, 255, 255), width=10)

    for element in user_audio_line:
        point1 = int(element[0])
        point2 = int(element[1])
        d.line([(point1 + 20, 270), (point2, 270)], fill=(76, 217, 100), width=10)
        
    d.text((10, 200), transcript, fill='white', font=font)
    d.text((40, 70), "Rhythm of English", fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='JPEG')

    elapsed = time.time() - start
    print('Elapsed time for generating rhythm image: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, user_audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    return buf.getvalue()

def upload_image(context, buf, user_audio_filename, suffix):
    start = time.time()
    key = 'report_images/' + os.path.splitext(os.path.basename(user_audio_filename))[0] + suffix + '.jpg'
    s3.put_object(ACL='public-read', Bucket=context['s3_bucket'], Key=key, Body=io.BytesIO(buf), ContentType='image/jpeg')
    elapsed = time.time() - start
    print('Elapsed time for uploading image: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, key, context['report_uid'], context['user_story_uid'], context['request_id']))
    return key

def download_audio(context, audio_filename):
    print("start download_audio")
    start = time.time()
    print("here in download_audio")
    system_filename = '/report_images/' + os.path.basename(audio_filename)
    print("system_filename")
    print(system_filename)
    print("context['s3_bucket']")
    print(context['s3_bucket'])
    s3.download_file(context['s3_bucket'], audio_filename, system_filename)
    print(audio_filename)
    print("got past download")
    elapsed = time.time() - start
    print('Elapsed time for downloading audio: {:.3f} key:{} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, audio_filename, context['report_uid'], context['user_story_uid'], context['request_id']))
    return system_filename

def generate_image_key(original_key, suffix):
    return 'report_images/' + os.path.splitext(os.path.basename(original_key))[0] + suffix + '.jpg'

def get_text_size(transcript, font):
    img = Image.new('RGB', (1000, 450), color = (20, 20, 20))
    d = ImageDraw.Draw(img)
    return d.textsize(transcript, font=font)

def write_transcript_to_file(transcript, audio_filename):
    transcript_filename = '/report_images/' + os.path.splitext(os.path.basename(audio_filename))[0] + '.txt'
    
    with open(transcript_filename, 'w') as f:
        f.write(transcript)

    return transcript_filename

def generate_report_images(context, data):

    start = time.time()
    print("data")
    print(data)
    print("step 0")
    report_scores = []
    report_images = []
    print("step 1")
    context = {
        'request_id': context['request_id'],
        's3_bucket': data['s3_bucket'],
        'report_uid': data['report_uid'],
        'callback_url': data['callback_url'],
        'user_story_uid': data['user_story_uid']
    }
    print("step 2")
    font = ImageFont.truetype('/report_images/OpenSans-Bold.ttf', 30)

    for story_scene_response in data['story_scene_responses']:
        print("step 3")
        master_audio_filename = story_scene_response['master']['audio_filename']
        transcript = story_scene_response['master']['audio_text']
        user_audio_filename = story_scene_response['user']['audio_filename']
        story_scene_user_response_id = story_scene_response['user']['story_scene_user_response_id']
        print("step 4")
        # write transcript to file to use with forced aligner
        transcript_filename = write_transcript_to_file(transcript, master_audio_filename)
        print("step 5")
        textSize = get_text_size(transcript, font)
        print("step 6")
        audio_system_filename = download_audio(context, master_audio_filename)
        print("step 6.5")
        master_start_end_times = parse_audio(context, master_audio_filename, audio_system_filename, transcript, transcript_filename)
        print("step 7")
        # master audio lines
        normalized_start = (master_start_end_times[0][0], master_start_end_times[0][0])
        master_audio_line, master_audio_heights = generate_audio_line(master_start_end_times, normalized_start, textSize)
        print("step 8")
        audio_system_filename = download_audio(context, user_audio_filename)
        user_start_end_times = parse_audio(context, user_audio_filename, audio_system_filename, transcript, transcript_filename)
        print("step 9")
        ## user audio lines
        normalized_start = (user_start_end_times[0][0], user_start_end_times[0][0])
        user_audio_line, user_audio_heights = generate_audio_line(user_start_end_times, normalized_start, textSize)
        print("step 10")
        b, score = generate_stress_image(context, master_audio_heights, user_audio_heights, transcript, textSize, font, user_audio_filename)
        image_key = upload_image(context, b, user_audio_filename, '_stress')
        report_image = {
             'story_scene_user_response_id': story_scene_user_response_id,
             'image_filename': image_key,
             'image_type': 'stress'
             #'story_scene_user_response_score' = score
        }
        print("step 11")
        report_images.append(report_image)
        report_scores.append(score)
        print("step 12")
        b = generate_rhythm_image(context, master_audio_line, user_audio_line, transcript, textSize, font, user_audio_filename)
        image_key = upload_image(context, b, user_audio_filename, '_rhythm')
        report_image = {
             'story_scene_user_response_id': story_scene_user_response_id,
             'image_filename': image_key,
             'image_type': 'rhythm',
             #'story_scene_user_response_score' = score
        }
        print("images")
        print(report_image)
        report_images.append(report_image)

    if context['callback_url']:
        payload = {
            'report_uid': data['report_uid'],
            'user_story_uid': data['user_story_uid'],
            'score': sum(report_scores)/len(report_scores),
            'report_images': report_images
        }
        print("payload")
        print(payload)
        send_callback(context, payload)
    print("start tracking time")
    elapsed = time.time() - start
    print('Elapsed time for generating report images function: {:.3f} report_uid:{} user_story_uid:{} request_id:{}'.format(elapsed, context['report_uid'], context['user_story_uid'], context['request_id']))

if __name__ == "__main__":
    try:
        resp = requests.get(sys.argv[1])
        data = resp.json()
        print("made it to report code")
        app_context = { 'request_id': str(uuid.uuid4()) }
        generate_report_images(app_context, data)
    except Exception as e:
        print(e)
