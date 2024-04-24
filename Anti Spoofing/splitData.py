import os
import random
import shutil
from itertools import islice

outFolderPath = "Dataset/SplitData"
inputFolderPath = "Dataset/DataCollect"
classes = ["fake", "real"]


try:
    shutil.rmtree(outFolderPath)
    print("Removed Directory")

except OSError as e:
    os.mkdir(outFolderPath)


# 創建目錄
os.makedirs(f"{outFolderPath}/train/images", exist_ok=True)
os.makedirs(f"{outFolderPath}/train/labels", exist_ok=True)
os.makedirs(f"{outFolderPath}/val/images", exist_ok=True)
os.makedirs(f"{outFolderPath}/val/labels", exist_ok=True)
os.makedirs(f"{outFolderPath}/test/images", exist_ok=True)
os.makedirs(f"{outFolderPath}/test/labels", exist_ok=True)


# 取得名字
listNames = os.listdir(inputFolderPath)
print(listNames)
print(len(listNames))  # 確認收集到的樣本數
uniqueNames = []
for name in listNames:
    uniqueNames.append(name.split('.')[0])
uniqueNames = list(set(uniqueNames))
print(len(uniqueNames))

# 隨機
random.shuffle(uniqueNames)
print(uniqueNames)

# 分配數量
lenData = len(uniqueNames)
lenTrain = int(lenData*0.7)
lenVal = int(lenData*0.2)
lenTest = int(lenData*0.1)
print(f'Total Images:{lenData}\n split:{lenTrain} {lenVal} {lenTest}')

if lenData != lenTrain+lenTest+lenVal:
    remaining = lenData-(lenTrain+lenTest+lenVal)
    lenTrain += remaining
print(f'Total Images:{lenData}\n split:{lenTrain} {lenVal} {lenTest}')
lengToSplit = [lenTrain, lenVal, lenTest]
Input = iter(uniqueNames)
Output = [list(islice(Input, elem)) for elem in lengToSplit]
print(
    f'Total Images:{lenData}\n split:{len(Output[0])} {len(Output[1])} {len(Output[2])}')

# 自動存進資料夾內
sequence = ['train', 'val', 'test']
for i, out in enumerate(Output):
    for fileName in out:
        shutil.copy(f'{inputFolderPath}/{fileName}.jpg',
                    f'{outFolderPath}/{sequence[i]}/images/{fileName}.jpg')
        shutil.copy(f'{inputFolderPath}/{fileName}.txt',
                    f'{outFolderPath}/{sequence[i]}/labels/{fileName}.txt')

print("Split Process Completed...")


dataYaml = f'path: ../Data\n\
train: ../train/images\n\
val: ../val/images\n\
test: ../test/images\n\
\n\
nc:{len(classes)}\n\
names:{classes}'

f = open(f'{outFolderPath}/data.yaml', 'a')
f.write(dataYaml)
f.close()

print("Data.yaml file Created...")
