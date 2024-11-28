from .pdxscript import get, format, Pair, Collection

vanilla_path = "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/"

def parse_focus_file(file_from, file_to):
    focus = open(file_to, "r", encoding="utf-8-sig")
    focus_data = get(focus.read()).get().val()
    
    with open(file_from, "r", encoding="utf-8-sig") as file:
        data = get(file.read()).get().val()

        for x in data:
            try:
                id = x.get().get("id").val()

                replaced = False
                for y in focus_data:
                    try:
                        if id == y.get().get("id").val():
                            
                            for objx in x.get().val():
                                replaced_2 = False
                                for objy in y.get().val():
                                    if objx[0] == objy[0]:
                                        objy.get().set(objx.get())
                                        replaced_2 = True
                                if not replaced_2:
                                    y.get().val().append(objx)

                            #y.set(x.get())

                            replaced = True
                            break

                    except: pass

                if not replaced:
                    focus_data.append(x)

            except: pass

        collected = Collection()
        collected.append(Pair("focus_tree", "=", focus_data))
        
        with open(file_from.replace(".focus", ".txt"), "w") as file:
            file.write(format(collected))

    focus.close()

