# user_service.py
from extensions import db, ma as marshmallow
# from flask import jsonify, request
from flask import current_app, jsonify, request
from sqlalchemy import exc, or_
from src.user_management_module.models.User import *
from src.user_management_module.models.Role import *
from src.user_management_module.models.Permissions import *
from src.user_management_module.models.EmployeeLog import EmployeeLog
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm.attributes import flag_modified
import random, string
from math import radians, cos, sin, asin, sqrt

IST = timezone(timedelta(hours=5, minutes=30))

class UserService:

    @staticmethod
    def getCountries():
        # minimal static list. You can expand or read from a file/db
        return jsonify(["India", "USA", "UK"])

    @staticmethod
    def getStates(country):
        data = {
            "India": ["Karnataka", "Maharashtra", "Tamil Nadu"],
            "USA": ["California", "Texas"],
            "UK": ["England", "Wales"]
        }
        return jsonify(data.get(country, []))

    @staticmethod
    def getDistricts(state):
        data = {
            "Karnataka": ["Bengaluru Urban", "Mysuru"],
            "Maharashtra": ["Pune", "Mumbai"]
        }
        return jsonify(data.get(state, []))

    @staticmethod
    def login():
        print("7777777777777777")
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        current_ip = request.remote_addr

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        try:
            # 🔥 ensure this code runs within the Flask app context
            with current_app.app_context():
                user = User.query.filter_by(username=username).first()

                if not user or user.password != password:
                    return jsonify({"error": "Invalid username or password."}), 400

                # Update user meta
                user.last_login_at = datetime.now(IST)
                user.current_login_ip = current_ip
                user.login_count = (user.login_count or 0) + 1

                now = datetime.now(IST)
                login_log = {
                    "id": 1,
                    "status": "login",
                    "datetime": now.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude
                }

                employee_log = EmployeeLog(
                    user_id=user.id,
                    loggin_logout=[{
                        "id": 1,
                        "status": "login",
                        "datetime": now.isoformat()
                    }],
                    location_logs=[login_log]
                )

                db.session.add(employee_log)
                db.session.commit()

                user_data = user_schema.dump(user)
                return jsonify(user_data), 200

        except Exception as ex:
            db.session.rollback()
            print("🔥 ERROR in login():", ex)
            return jsonify({"error": str(ex)}), 500

    @staticmethod
    def logout():
        data = request.get_json() or {}
        user_id = data.get("user_id")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        current_ip = request.remote_addr

        if not user_id:
            return jsonify({"error": "user_id is required for logout."}), 400

        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "Invalid user ID."}), 400

            user.last_login_at = datetime.now(IST)
            user.current_login_ip = current_ip

            last_log = EmployeeLog.query.filter_by(user_id=user.id).order_by(EmployeeLog.id.desc()).first()
            if not last_log:
                return jsonify({"error": "No active session found for this user."}), 400

            logins = last_log.loggin_logout or []
            if not logins or logins[-1]['status'] == 'logout':
                return jsonify({"error": "No login session found in the logs or already logged out."}), 400

            now = datetime.now(IST)
            logout_log = {
                "id": len(logins)+1,
                "status": "logout",
                "datetime": now.isoformat()
            }
            logins.append(logout_log)

            locations = last_log.location_logs or []
            logout_location = {
                "id": len(locations)+1,
                "status": "logout",
                "datetime": now.isoformat(),
                "latitude": latitude,
                "longitude": longitude
            }
            locations.append(logout_location)

            last_log.loggin_logout = logins
            last_log.location_logs = locations

            flag_modified(last_log, "loggin_logout")
            flag_modified(last_log, "location_logs")
            db.session.commit()

            return jsonify({"message": "Logged out successfully"})
        except Exception as ex:
            db.session.rollback()
            return jsonify({"error": str(ex)}), 500

    @staticmethod
    def addLocationPoint():
        data = request.get_json() or {}
        user_id = data.get("user_id")
        status = data.get("status")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        duration = data.get("duration")
        takentime = data.get("takentime")
        starttime = data.get("starttime")
        reachedtime = data.get("reachedtime")

        if not user_id or latitude is None or longitude is None or not status:
            return jsonify({"error": "user_id, latitude, longitude and status are required."}), 400

        try:
            last_log = EmployeeLog.query.filter_by(user_id=user_id).order_by(EmployeeLog.id.desc()).first()
            if not last_log:
                new_log = EmployeeLog(
                    user_id=user_id,
                    loggin_logout=[],
                    location_logs=[],
                )
                db.session.add(new_log)
                db.session.commit()
                last_log = new_log

            locations = last_log.location_logs or []
            now = datetime.now(IST)
            loc_entry = {
                "id": len(locations)+1,
                "status": status,
                "longitude": longitude,
                "latitude": latitude,
                "datetime": now.isoformat()
            }
            if status == "static":
                loc_entry["duration"] = duration
                loc_entry["starttime"] = starttime
                loc_entry["reachedtime"] = reachedtime
                loc_entry["takentime"] = takentime

            locations.append(loc_entry)
            last_log.location_logs = locations
            flag_modified(last_log, "location_logs")
            db.session.commit()
            return jsonify({"message": "Location saved"})
        except Exception as ex:
            db.session.rollback()
            return jsonify({"error": str(ex)}), 500

    @staticmethod
    def generate_fs_uniquifier(length=10):
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        return ''.join(random.choices(characters, k=length))

    @staticmethod
    def getAllUsers():
        try:
            users = User.query.order_by(User.username.asc()).all()
            return users_schema.dump(users)
        except exc.InternalError:
            return jsonify({"error": "Internal error fetching users"}), 500

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(min(1, sqrt(a)))
        R = 6371000
        return R * c

    @staticmethod
    def process_locations(points, stop_radius_m=20):
        if not points:
            return {"path": [], "stops": [], "movements": []}
        normalized = []
        for p in points:
            lat = float(p.get("lat") or p.get("latitude"))
            lng = float(p.get("lng") or p.get("longitude"))
            ts_raw = p.get("ts") or p.get("timestamp") or p.get("time") or p.get("datetime")
            if isinstance(ts_raw, str):
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).astimezone(IST)
            elif isinstance(ts_raw, (int, float)):
                ts = datetime.fromtimestamp(float(ts_raw), tz=timezone.utc).astimezone(IST)
            else:
                ts = datetime.now(IST)
            normalized.append({"lat": lat, "lng": lng, "ts": ts})
        normalized.sort(key=lambda x: x["ts"])
        path = [[p["lat"], p["lng"]] for p in normalized]
        stops = []
        movements = []
        i = 0
        n = len(normalized)
        while i < n:
            j = i + 1
            stop_points = [normalized[i]]
            while j < n:
                d = UserService.haversine(
                    normalized[j]["lat"], normalized[j]["lng"],
                    normalized[j-1]["lat"], normalized[j-1]["lng"]
                )
                if d <= stop_radius_m:
                    stop_points.append(normalized[j])
                    j += 1
                else:
                    break
            start_ts = stop_points[0]["ts"]
            end_ts = stop_points[-1]["ts"]
            duration_seconds = (end_ts - start_ts).total_seconds()
            if len(stop_points) > 1 and duration_seconds >= 30:
                avg_lat = sum(p["lat"] for p in stop_points) / len(stop_points)
                avg_lng = sum(p["lng"] for p in stop_points) / len(stop_points)
                duration_minutes = duration_seconds / 60.0
                if duration_minutes <= 5:
                    color_label = "black"
                elif duration_minutes <= 10:
                    color_label = "yellow"
                elif duration_minutes <= 15:
                    color_label = "orange"
                else:
                    color_label = "red"
                stops.append({
                    "lat": avg_lat,
                    "lng": avg_lng,
                    "start_ts": start_ts.isoformat(),
                    "end_ts": end_ts.isoformat(),
                    "duration_minutes": round(duration_minutes, 2),
                    "color_label": color_label
                })
                i = j
            else:
                if i + 1 < n:
                    frm = normalized[i]
                    to = normalized[i+1]
                    duration_minutes = (to["ts"] - frm["ts"]).total_seconds() / 60.0
                    distance_m = UserService.haversine(frm["lat"], frm["lng"], to["lat"], to["lng"])
                    movements.append({
                        "from": {"lat": frm["lat"], "lng": frm["lng"], "ts": frm["ts"].isoformat()},
                        "to": {"lat": to["lat"], "lng": to["lng"], "ts": to["ts"].isoformat()},
                        "duration_minutes": round(duration_minutes, 2),
                        "distance_m": round(distance_m, 2)
                    })
                i += 1
        return {"path": path, "stops": stops, "movements": movements}

    @staticmethod
    def getEmployeeLocations(user_id):
        if not user_id:
            return jsonify({"error": "user_id is required."}), 400
        try:
            logs = EmployeeLog.query.filter_by(user_id=user_id).order_by(EmployeeLog.id.desc()).all()
            if not logs:
                return jsonify({"path": [], "stops": [], "movements": [], "raw": []})
            latest = logs[0]
            raw_points = latest.location_logs or []
            for p in raw_points:
                ts_raw = p.get("ts") or p.get("datetime")
                if isinstance(ts_raw, str):
                    p["ts"] = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).astimezone(IST).isoformat()
                elif isinstance(ts_raw, (int, float)):
                    p["ts"] = datetime.fromtimestamp(float(ts_raw), tz=timezone.utc).astimezone(IST).isoformat()
                else:
                    p["ts"] = datetime.now(IST).isoformat()
            processed = UserService.process_locations(raw_points)
            return jsonify({
                "path": processed["path"],
                "stops": processed["stops"],
                "movements": processed["movements"],
                "raw": raw_points
            })
        except exc.SQLAlchemyError:
            return jsonify({"error": "Error fetching employee locations."}), 500

    @staticmethod 
    def getLoggedInUsers():
        """
        Returns users who have logged in today (at least one login event for current date).
        """
        today = datetime.now(IST).date()
        users = []
        all_users = User.query.all()
        for user in all_users:
            log = EmployeeLog.query.filter_by(user_id=user.id).order_by(EmployeeLog.id.desc()).first()
            if not log:
                continue
            logins = log.loggin_logout or []
            for entry in logins:
                if entry.get('status') == 'login':
                    dt_str = entry.get('datetime')
                    if dt_str:
                        try:
                            dt = datetime.fromisoformat(dt_str).astimezone(IST)
                            if dt.date() == today:
                                users.append(user)
                                break
                        except Exception:
                            continue
        return users_only_schema.dump(users)
    
    @staticmethod 
    def getPendingLeaves():
        """
        Returns full EmployeeLog rows (including all columns and nested JSON fields)
        for employees who have pending leaves valid for today or future.
        """
        today = datetime.now(IST).date().isoformat()
        logs_out = []
        users = {u.id: u for u in User.query.all()}

        # Iterate through employee logs
        for log in EmployeeLog.query.order_by(EmployeeLog.id.desc()).all():
            user = users.get(log.user_id)
            if not user or not hasattr(log, 'leave') or not log.leave:
                continue

            # Filter pending/future leaves
            pending_leaves = []
            for leave in log.leave:
                if leave.get("status") == "pending":
                    from_date = leave.get("from_date")
                    to_date = leave.get("to_date")
                    if (from_date and from_date >= today) or (to_date and to_date >= today):
                        pending_leaves.append(leave)

            # Skip logs with no relevant leaves
            if not pending_leaves:
                continue

            # Update log with filtered leaves
            log_data = {
                "id": log.id,
                "user_id": log.user_id,
                "loggin_logout": log.loggin_logout,
                "location_logs": log.location_logs,
                "leave": pending_leaves,
                "break_time": getattr(log, "break_time", None)
            }

            # Merge user details
            log_data.update({
                "employee_name": f"{user.first_name} {getattr(user, 'last_name', '')}".strip(),
                "username": user.username,
                "email": getattr(user, "email", ""),
                "state": getattr(user, "state", ""),
                "district": getattr(user, "district", ""),
                "department": getattr(user, "department", ""),
                "role": getattr(user, "role", "")
            })

            logs_out.append(log_data)

        return jsonify(logs_out)
    
    @staticmethod 
    def approveLeave(payload):
        """
        Approves a leave for a user, status='approved', updates in JSON array.
        Finds by log id (row id), employee_id (user_id), leave_id (int).
        """
        log_id = payload.get('id')  # This is the employee_log row id!
        employee_id = payload.get('employee_id')
        leave_id = payload.get('leave_id')
        approvedby = payload.get('approvedby')

        if log_id is None or employee_id is None or leave_id is None or not approvedby:
            raise BadRequest("id, employee_id, leave_id, and approvedby are required.")

        try:
            leave_id = int(leave_id)
        except (ValueError, TypeError):
            raise BadRequest("leave_id must be an integer.")

        # 1. Locate the correct EmployeeLog row for this action
        log = EmployeeLog.query.filter_by(id=log_id, user_id=employee_id).first()
        if not log or not hasattr(log, 'leave') or not log.leave:
            raise BadRequest("Leave not found for employee.")

        # 2. Update the specific leave (by leave_id)
        leaves = []
        updated = False
        for leave in log.leave:
            # Defensive: cast ID as int for comparison
            if int(leave.get("leave_id", -1)) == leave_id:
                if leave.get("status") != "pending":
                    raise BadRequest("Only pending leaves can be approved.")
                leave = leave.copy()
                leave["status"] = "approved"
                leave["approvedby"] = approvedby
                leave["approveddatetime"] = datetime.now(IST).isoformat()
                updated = True
            leaves.append(leave)

        if not updated:
            raise BadRequest("Leave not found for employee.")

        # 3. Write the new array back & commit
        log.leave = leaves
        flag_modified(log, "leave")
        db.session.commit()

        return jsonify({
            "message": "Leave approved",
            "leave_id": leave_id,
            "employee_id": employee_id
        })
    
    @staticmethod 
    def addLeave(payload):
        """
        Adds a leave log: {leave_id, from_date, to_date, reason, status:'pending', createddatetime}
        """
        try:
            user_id = payload.get("user_id")
            from_date = payload.get("from_date")
            to_date = payload.get("to_date")
            reason = payload.get("reason")
            
            if not user_id or not from_date or not to_date or not reason:
                raise BadRequest("user_id, from_date, to_date, and reason are required.")

            # Use latest EmployeeLog for user, or create one if none exists
            last_log = EmployeeLog.query.filter_by(user_id=user_id).order_by(EmployeeLog.id.desc()).first()
            if not last_log:
                last_log = EmployeeLog(user_id=user_id, loggin_logout=[], location_logs=[], leave=[])
                db.session.add(last_log)
                db.session.flush()  # Ensure log has an ID before committing
            
            # Initialize leave list if not exists
            if not hasattr(last_log, "leave") or last_log.leave is None:
                last_log.leave = []
            
            leaves = last_log.leave
            
            # Generate sequential leave_id: find max existing ID and add 1
            if leaves:
                max_id = max(leave.get('leave_id', 0) for leave in leaves)
                leave_id = max_id + 1
            else:
                leave_id = 1
            
            leave_entry = {
                "leave_id": leave_id,  # Sequential numeric ID
                "from_date": from_date,
                "to_date": to_date,
                "reason": reason,
                "status": "pending",
                "createddatetime": datetime.now(IST).isoformat()
            }
            
            leaves.append(leave_entry)
            last_log.leave = leaves
            flag_modified(last_log, "leave")
            db.session.commit()
            
            return jsonify({
                "message": "Leave request saved",
                "leave_id": leave_id  # Return the leave_id
            })

        except BadRequest as br:
            db.session.rollback()
            raise br
        except Exception as ex:
            db.session.rollback()
            raise InternalServerError(f"Error adding leave: {str(ex)}")

    @staticmethod 
    def addBreak(payload):
        """
        Adds a break entry in the 'break_time' list: {id, status:"break", startdatetime, enddatetime (optional/null), reason}
        """
        try:
            user_id = payload.get("user_id")
            reason = payload.get("reason")
            startdatetime = payload.get("startdatetime")
            enddatetime = payload.get("enddatetime") if "enddatetime" in payload else None

            if not user_id or not reason or not startdatetime:
                raise BadRequest("user_id, reason, startdatetime required.")

            last_log = EmployeeLog.query.filter_by(user_id=user_id).order_by(EmployeeLog.id.desc()).first()
            if not last_log:
                last_log = EmployeeLog(user_id=user_id, loggin_logout=[], location_logs=[])
                db.session.add(last_log)
                db.session.commit()

            # --- Use 'break_time' JSON column ---
            if not hasattr(last_log, "break_time") or last_log.break_time is None:
                last_log.break_time = []
            break_time = last_log.break_time

            break_entry = {
                "id": len(break_time) + 1,
                "status": "break",
                "startdatetime": startdatetime,
                "enddatetime": enddatetime,
                "reason": reason
            }
            break_time.append(break_entry)
            last_log.break_time = break_time
            flag_modified(last_log, "break_time")
            db.session.commit()

            return jsonify({"message": "Break logged"})

        except Exception as ex:
            db.session.rollback()
            raise InternalServerError(f"Error logging break: {str(ex)}")

    @staticmethod 
    def endBreak(payload):
        """
        Update latest open break for user by setting its 'enddatetime' (in break_time column only)
        Multiple breaks per day/user are supported.
        """
        try:
            user_id = payload.get("user_id")
            enddatetime = payload.get("enddatetime")
            if not user_id or not enddatetime:
                raise BadRequest("user_id and enddatetime are required.")

            last_log = EmployeeLog.query.filter_by(user_id=user_id).order_by(EmployeeLog.id.desc()).first()
            if not last_log:
                raise BadRequest("No break found for user.")

            # --- Update latest open break in 'break_time' ---
            if not hasattr(last_log, "break_time") or last_log.break_time is None:
                last_log.break_time = []
            break_time = last_log.break_time

            updated = False
            for entry in reversed(break_time):
                if (
                    entry.get("status") == "break"
                    and (entry.get("enddatetime") in (None, "", "null"))
                ):
                    entry["enddatetime"] = enddatetime
                    updated = True
                    break

            if updated:
                last_log.break_time = break_time
                flag_modified(last_log, "break_time")
                db.session.commit()
                return jsonify({"message": "Break ended"})
            else:
                raise BadRequest("No open break found to end.")

        except Exception as ex:
            db.session.rollback()
            raise InternalServerError(f"Error ending break: {str(ex)}")
        
    @staticmethod
    def CreateUser():
        try:
            user = UserService.getUserActionLogObjectFromJson()
            existing_user = db.session.query(User).filter(or_(User.email == user.email,User.username == user.username,User.employee_code == user.employee_code)).first()
            if existing_user:
                conflict_fields = []
                if existing_user.email == user.email:
                    conflict_fields.append("email")
                if existing_user.username == user.username:
                    conflict_fields.append("username")
                if existing_user.employee_code == user.employee_code:
                    conflict_fields.append("employee_code")
                raise BadRequest(f"Duplicate value found for: {', '.join(conflict_fields)}")
            user.fs_uniquifier = UserService.generate_fs_uniquifier()
            db.session.add(user)
            db.session.commit()
            return "User Created Successfully!!"
        except exc.InternalError:
            raise InternalServerError
    
    @staticmethod
    def getUserById(id):
        """
        Fetches user by userId
        """
        try:
            user = User.query.get(id)
            if user.id:
                return user_schema.dump(user)
        except AttributeError:
            raise UserNotExistsError
        except exc.InternalError:
            raise InternalServerError
        
    @staticmethod
    def updateUser(userId):
        """
        Update User Details
        """
        try:
            # Get the new details from request
            user_update = UserService.getJSON()
            log.info('Updates User record: %s' % (userId))

            # Fetch existing user record
            userDetails = security.datastore.find_user(id=userId)
            if userDetails:
                # Update the user fields (matching your model)
                if 'email' in user_update:
                    userDetails.email = user_update['email']
                if 'username' in user_update:
                    userDetails.username = user_update['username']
                if 'employee_code' in user_update:
                    userDetails.employee_code = user_update['employee_code']
                # Add other fields as needed

                db.session.commit()
                return {"message": "User Updated Successfully"}
            else:
                return {"message": "User doesn't exist"}
        except exc.InternalError:
            raise InternalServerError
        
    @staticmethod
    def getEmployeeLogsData(payload):
        """
        Returns location logs + leaves summary for a date range.
        Responds with:
        {
          "date_range": "YYYY-MM-DD to YYYY-MM-DD",
          "leaves_approved": int,
          "leaves_pending": int,
          "logs": [
            {"latitude": str, "longitude": str, "datetime": str, "status": str}
          ]
        }
        """
        try:
            user_id = payload.get("user_id")
            from_date = payload.get("from_date")
            to_date = payload.get("to_date")

            if not user_id or not from_date or not to_date:
                raise BadRequest("user_id, from_date, and to_date are required.")

            logs = EmployeeLog.query.filter_by(user_id=user_id).all()

            filtered_logs = []
            leaves_in_range = []
            for log in logs:
                locations = log.location_logs or []
                for entry in locations:
                    log_date_str = entry.get("datetime", "")[:10]
                    if from_date <= log_date_str <= to_date:
                        filtered_logs.append(entry)
                        leave_list = entry.get("leave", [])
                        for leave_entry in leave_list:
                            leave_date = leave_entry.get("date")
                            leave_status = leave_entry.get("status")
                            if leave_date and from_date <= leave_date <= to_date:
                                leaves_in_range.append(leave_status)

            approved_count = sum(1 for s in leaves_in_range if str(s or "").lower() == "approved")
            pending_count = sum(1 for s in leaves_in_range if str(s or "").lower() == "pending")

            # Format log output for frontend table if needed
            def fmt_latlng(val):
                try:
                    return f"{float(val):.6f}"
                except:
                    return "-"
            def fmt_datetime(dt):
                try:
                    if not dt:
                        return "-"
                    return datetime.fromisoformat(dt).strftime("%d-%m-%Y %H:%M")
                except:
                    return str(dt) or "-"

            logs_output = []
            for entry in filtered_logs:
                logs_output.append({
                    "latitude": fmt_latlng(entry.get("latitude", "")),
                    "longitude": fmt_latlng(entry.get("longitude", "")),
                    "datetime": fmt_datetime(entry.get("datetime", "")),
                    "status": entry.get("status", "-") or "-"
                })

            return jsonify({
                "date_range": f"{from_date} to {to_date}",
                "leaves_approved": approved_count,
                "leaves_pending": pending_count,
                "logs": logs_output
            })

        except Exception as ex:
            raise InternalServerError(f"Error fetching logs: {str(ex)}")

    @staticmethod
    def createRole():
        """
        Saves Role
        """
        try:
            json_data = connexion.request.get_json()
            if not json_data:
                return {"message": "No input data provided"}, 400
            validated_data = role_schema.load(json_data, session=db.session)
            role_data = Role(**validated_data)
            existing = Role.query.filter_by(role_code=role_data.role_code).first()
            if existing:
                return {"message": "Role already exists"}, 409
            db.session.add(role_data)
            db.session.commit()
            return {"message": "Role created successfully"}, 201
        except exc.IntegrityError:
            db.session.rollback()
            raise RoleAlreadyExistsError
        except exc.InternalError:
            db.session.rollback()
            raise InternalServerError

    @staticmethod
    def addPermissionsToRole():
        """
        Adds Permissions to an Existing Role
        """
        try:
            role = UserService.getJSON()
            if security.datastore.find_role(role['name']):
                roleobj = security.datastore.find_role(role['name'])
                print(", ".join(role['permissions']))
                security.datastore.add_permissions_to_role(roleobj, ", ".join(role['permissions']))
                db.session.commit()
                return {"message": "Permissions added"}
            else: 
                raise RoleNotFound
        except exc.IntegrityError:
            db.session.rollback()
            raise RoleAlreadyExistsError
        except exc.InternalError:
            raise InternalServerError
    
    @staticmethod
    def removePermissionsToRole():
        """
        Remove Permissions from Existing Role
        """
        try:
            role = UserService.getJSON()
            if security.datastore.find_role(role['name']):
                roleobj = security.datastore.find_role(role['name'])
                security.datastore.remove_permissions_from_role(roleobj, ", ".join(role['permissions']))
                db.session.commit()
                return {"message": "Permissions removed from Role"}
            else:
                raise RoleNotFound
        except exc.IntegrityError:
            db.session.rollback()
            raise RoleAlreadyExistsError
        except exc.InternalError:
            raise InternalServerError

    @staticmethod 
    def getRoles():
        """
        Retreives all Roles
        """
        try:
            roles = Role.query.order_by(Role.name.asc()).all()
            return roles_schema.dump(roles)
        except exc.InternalError:
            raise InternalServerError

    @staticmethod 
    def getRoleById(id):
        """
        Fetches role by roleId
        """
        try:
            role = Role.query.get(id)
            if role.id:
                return role_schema.dump(role)
        except AttributeError:
            raise RoleNotExistsError
        except exc.InternalError:
            raise InternalServerError
        
    @staticmethod
    def updatePermission(id):
        try:
            db.session.query(Permissions).filter(
                Permissions.id == id).update(UserService.getJSON())
            db.session.commit()
        except exc.InternalError:
            raise InternalServerError
        except exc:
            db.session.rollback()
            raise exc

    @staticmethod  
    def getPermissions():
        try:
            permission = Permissions.query.all()
            return permissions_schema.dump(permission)
        except exc.InternalError:
            raise InternalServerError
    
    @staticmethod
    def addNewPermission():
        """
        Saves Permission
        """
        try:
            json_data = connexion.request.get_json()
            if not json_data:
                return {"message": "No input data provided"}, 400
            validated_data = permissions_schema.load(json_data, session=db.session)
            permission_data = Permissions(**validated_data)
            existing = Permissions.query.filter_by(code=permission_data.code).first()
            if existing:
                return {"message": "Permissions already exists"}, 409
            db.session.add(permission_data)
            db.session.commit()
            return {"message": "Permissions created successfully"}, 201
        except exc.InternalError:
            raise InternalServerError
        
    @staticmethod
    def getRoleObjectFromJson():
        """
        Converts JSON To Role Object
        """
        data = Role(**UserService.getJSON())
        return data
    
    @staticmethod
    def getPermissionObjectFromJson():
        """
        Converts JSON To Role Object
        """
        data = Permissions(**UserService.getJSON())