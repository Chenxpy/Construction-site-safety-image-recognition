from ultralytics import YOLO

model = YOLO('yolo8n.pt')


def main():
    model.train(data='Dataset/SplitData/dataOffLine.yaml', epochs=3)


if __name__ == '__main__':
    main()
