import MySQLdb
from datetime import date, datetime, timedelta

def writeHealthDataServer(output_file, data_type):
  is_face = False
  is_temp = False
  skinTemp = -1.0
  lesionCountTotal = -1
  lesionAreaTotal = -1
  lesionCountRed = -1
  lesionAreaRed = -1
  lesionCountDark = -1
  lesionAreaDark = -1
  faceColor  = '#000000'
  
  #### READ DATA ####
  
  #open output file and read data
  if data_type == "thermal":
    file_dir = "thermal/output/" + output_file + ".txt"
    with open(file_dir) as fp:
      for i, line in enumerate(fp):
        line = line.rstrip()
        if i == 0:
          skinTemp = float(line)
          if skinTemp > 0:
            is_temp = True
            #print(skinTemp)
          else:
            break
        elif i > 0:
          break
  elif data_type == "color":
    file_dir = "color/output/" + output_file + ".txt"
    with open(file_dir) as fp:
      for i, line in enumerate(fp):
        line = line.rstrip()
        if i == 0:
          if line == "yes":
            print("yes face")
            is_face = True
          else:
            print("no face")
            break
        elif i == 1:
          lesionCountTotal = int(line)
          #print(lesionCountTotal)
        elif i == 2:
          lesionAreaTotal = int(line)
         # print(lesionAreaTotal)
        elif i == 3:
          lesionCountRed = int(line)
         # print(lesionCountRed)
        elif i == 4:
          lesionAreaRed = int(line)
          #print(lesionAreaRed)
        elif i == 5:
          lesionCountDark = int(line)
          #print(lesionCountDark)
        elif i == 6:
          lesionAreaDark = int(line)
          #print(lesionAreaDark)
        elif i == 7:
          faceColor = line
          #print(faceColor)
        elif i > 7:
          break
  
  #### WRITE TO SERVER ####
  if (is_face == True) | (is_temp == True):
    # Open database connection, prepare cursor
    conn = MySQLdb.connect(host= "smartmirror.crgjuzhhi5bw.us-east-1.rds.amazonaws.com",
                  user="SmartMirrorUser",
                  passwd="ECEN403909",
                  db="SmartMirror")
    cursor = conn.cursor()
    
    #Get timestamp and use it to insert new row if possible
    insert_stmt_time = (
    "INSERT IGNORE INTO austin (timestamp) "
    "VALUES (%s)"
    )
    timestamp = datetime.now().date()
    #timestamp = datetime.now().date() + timedelta(days=1) #tomorrow
    cursor.execute(insert_stmt_time, (timestamp,))
    
    #Write the data
    if (data_type == "thermal"):
      update_thrml_data_stmt = (""" 
      UPDATE austin 
      SET skinTemp = %s
      WHERE timestamp = %s """
      )
      data_thrml = (skinTemp, timestamp)
      cursor.execute(update_thrml_data_stmt, data_thrml)
    elif (data_type == "color"):
      update_color_data_stmt = (""" 
      UPDATE austin 
      SET lesionCountTotal = %s, lesionAreaTotal = %s, lesionCountRed = %s, lesionAreaRed = %s, lesionCountDark = %s, lesionAreaDark = %s, faceColor = %s
      WHERE timestamp = %s """
      )
      data_color = (lesionCountTotal, lesionAreaTotal, 
        lesionCountRed, lesionAreaRed, lesionCountDark, lesionAreaDark, faceColor, timestamp )
      cursor.execute(update_color_data_stmt, data_color)
    
    #commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
  else:
    print("not writing to database: no face detected or error with skin temperature")