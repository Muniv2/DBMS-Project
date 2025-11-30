# quick_upload_test.py
print("🚀 QUICK UPLOAD TEST STARTING...")

try:
    # Test 1: Basic imports
    from database import Database
    print("✅ Database import successful")
    
    # Test 2: Upload module import
    from modules.uploader.upload import UploadWindow
    print("✅ UploadWindow import successful")
    
    # Test 3: Dashboard import  
    from modules.uploader.dashboard import UploadWindow
    print("✅ UploaderDashboard import successful")
    
    print("\n🎉 ALL IMPORTS WORKING!")
    
    # Test 4: Quick database test
    db = Database()
    if db.connection:
        print("✅ Database connection working")
        
        # Test 5: Try a simple upload
        print("\n🧪 Testing upload functionality...")
        try:
            # This is what happens when user clicks upload
            song_query = """
            INSERT INTO Song (songName, genre, paid, price, songFile, songViewCount, songLikeCount)
            VALUES (?, ?, ?, ?, ?, 0, 0)
            """
            
            # Test data
            result = db.execute_query(song_query, ("Quick Test Song", "Test", 0, 0.0, "test.mp3"))
            
            if result:
                print("✅ Song inserted successfully!")
                
                # FIX: Use proper ID retrieval method
                print("🔍 Getting auto-generated song ID...")
                
                # Method 1: Try @@IDENTITY first
                id_result = db.execute_query("SELECT @@IDENTITY")
                if id_result and id_result[0][0]:
                    song_id = int(id_result[0][0])
                    print(f"✅ Song ID found using @@IDENTITY: {song_id}")
                else:
                    # Method 2: Try SCOPE_IDENTITY()
                    id_result = db.execute_query("SELECT SCOPE_IDENTITY()")
                    if id_result and id_result[0][0]:
                        song_id = int(id_result[0][0])
                        print(f"✅ Song ID found using SCOPE_IDENTITY: {song_id}")
                    else:
                        # Method 3: Get the latest ID
                        id_result = db.execute_query("SELECT MAX(songID) FROM Song")
                        if id_result and id_result[0][0]:
                            song_id = int(id_result[0][0])
                            print(f"✅ Song ID found using MAX: {song_id}")
                        else:
                            print("❌ Could not get song ID using any method")
                            song_id = None
                
                if song_id:
                    # Create upload relationship
                    print(f"🔗 Creating upload relationship for song ID: {song_id}")
                    upload_result = db.execute_query("INSERT INTO Upload (HUID, songID) VALUES (?, ?)", (1, song_id))
                    if upload_result:
                        print("✅ Upload relationship created!")
                        
                        # Verify everything worked
                        verify = db.execute_query("""
                            SELECT s.songID, s.songName, u.HUID 
                            FROM Song s 
                            JOIN Upload u ON s.songID = u.songID 
                            WHERE s.songID = ?
                        """, (song_id,))
                        
                        if verify:
                            print(f"🎉 VERIFIED: Song '{verify[0][1]}' (ID: {verify[0][0]}) uploaded by user {verify[0][2]}")
                        else:
                            print("⚠️ Could not verify upload")
                    else:
                        print("❌ Upload relationship failed")
                else:
                    print("❌ No song ID available for upload relationship")
                    
            else:
                print("❌ Song insert failed")
                
        except Exception as e:
            print(f"❌ Upload test error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Database connection failed")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("💡 Check your file structure and class names")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ TEST COMPLETED")