import json, os

levelDict = {
    "level":[["#"]*20,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*1 + ["_"]*18 + ["#"]*1,
              ["#"]*20],
    "decoderRing" : {
                    "_" : "floor",
                    "#" : "wall"}
}

if True:
    filePath = os.path.join(os.path.dirname(__file__),"testLevelF.lvl")
    print(filePath)
    with open(filePath, "w") as data_file:
        json.dump(levelDict, data_file)
    data_file.close()

    with open(filePath, "r") as data_file:
        thing = json.load(data_file)
    data_file.close()
    print(thing["decoderRing"])

if False:
    jstring = json.dumps(levelDict)
    thing = json.loads(jstring)
    print(thing["decoderRing"])