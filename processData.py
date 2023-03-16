#!/usr/bin/env python3

from os.path import exists, join
from typing import List
from pprint import pprint
from uuid import uuid4
from json import dump


class Poem(object):
    def __init__(self, title: str, volume: int, id: int) -> None:
        self.title: str = title
        self.volume: int = volume
        self.id: int = id
        self.sentences: List[str] = list()
        self.author: str | None = None

    def addSentence(self, newSentence: str):
        if "__" in newSentence:
            # a sentence following author name
            sentence, author = newSentence.split("\\__")
            sentence = sentence.strip()
            if len(sentence.split("。")[-1]) == 1 or len(sentence.split("，")[-1]) == 1:
                sentence = sentence[0:-1]  # strip last character
            if sentence[-1] in ["。", "，"]:
                newSentence = f"{sentence[:-1]} （{author}）{sentence[-1]}"
            else:
                newSentence = f"{sentence.strip()} （{author}）"
        if newSentence.split("。")[-1].__len__() == 1:
            newSentence = newSentence[0:-1]  # strip last character
        self.sentences.append(newSentence)

    def __repr__(self) -> str:
        return f"Poem [{self.title}] in {self.volume} ID {self.id} by {self.author}"

    def dump(self):
        if self.author ==  None:
            self.author = '未知'
        return {
            "uuid": str(uuid4()),
            "volume": self.volume,
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "sentences": list(
                map(
                    lambda x: x + "。",
                    filter(lambda x: len(x) > 1, "".join(self.sentences).split("。")),
                )
            ),
        }


def process(fileName: str):
    poems: List[Poem] = list()
    currentPoemPointer: Poem | None = None

    titleStillProcessing: bool = False
    halfTitle: str = ""

    for index, i in enumerate(open(fileName, "r").readlines()):
        i = i.strip()
        i = i.replace("-", "_")
        if i == "" or i.isspace() or "《全唐诗》" in i:
            continue
        if i.startswith("卷") and "【" in i or titleStillProcessing:
            if i.split("】")[-1].__len__() != 0:
                volumeID, poemID, title, author = (
                    int(i.split("_")[0][1:]),
                    int(i.split("_")[1].split("【")[0]),
                    i.split("【")[1].split("】")[0],
                    i.split("】")[-1],
                )
                if currentPoemPointer is not None:
                    poems.append(currentPoemPointer)
                currentPoemPointer = Poem(title, volumeID, poemID)
                currentPoemPointer.author = author
                continue
            else:
                if titleStillProcessing:
                    i = halfTitle + i
                    halfTitle = ""
                if not "】" in i:
                    print(f"Warning: Invalid title line in {index}")
                    titleStillProcessing = True
                    halfTitle = i
                    continue
                volumeID, poemID, title = (
                    int(i.split("_")[0][1:]),
                    int(i.split("_")[1].split("【")[0]),
                    i.split("【")[1].strip("】\n"),
                )
                titleStillProcessing = False
                if currentPoemPointer is not None:
                    poems.append(currentPoemPointer)
                currentPoemPointer = Poem(title, volumeID, poemID)
                continue
        if currentPoemPointer is not None:
            if "。" not in i and "，" not in i:
                if currentPoemPointer.author is None:
                    currentPoemPointer.author = i
                    continue
            else:
                currentPoemPointer.addSentence(i)

    if currentPoemPointer is not None:
        poems.append(currentPoemPointer)
    return poems


if __name__ == "__main__":
    RESULT = list()
    for i in range(1, 900):
        targetFile = join("./", "src", f"{i}.raw")
        if not exists(targetFile):
            print(f"Error : File {targetFile} not found!")
            exit(1)
        for i in [i.dump() for i in process(targetFile)]:
            RESULT.append(i)
    with open("result.json", "w") as fp:
        dump(RESULT, fp, ensure_ascii=False)
        fp.flush()
        fp.close()
    print("Done.")
