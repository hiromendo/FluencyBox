FROM lowerquality/gentle

RUN pip install audioread boto3 Pillow requests

COPY OpenSans-Bold.ttf /report_images/OpenSans-Bold.ttf
COPY generate_report_images.py /report_images/generate_report_images.py

ENTRYPOINT ["python", "/report_images/generate_report_images.py"]
