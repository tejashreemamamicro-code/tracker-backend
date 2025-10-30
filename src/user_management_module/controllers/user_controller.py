# user_controller.py
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from src.user_management_module.services.user_service import UserService

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    print("********************s")
    return UserService.login()

@user_bp.route('/logout', methods=['POST'])
def logout():
    return UserService.logout()

@user_bp.route('/logged-in-users', methods=['GET'])
def getLoggedInUsers():
    return UserService.getLoggedInUsers()

@user_bp.route('/addLocationPoint', methods=['POST'])
def add_location_point():
    return UserService.addLocationPoint()

@user_bp.route('/user', methods=['GET'])
def get_all_users():
    return jsonify(UserService.getAllUsers())

@user_bp.route('/countries', methods=['GET'])
def get_countries():
    return UserService.getCountries()

@user_bp.route('/states/<country>', methods=['GET'])
def get_states(country):
    return UserService.getStates(country)

@user_bp.route('/districts/<state>', methods=['GET'])
def get_districts(state):
    return UserService.getDistricts(state)

@user_bp.route('/pending-leaves', methods=['GET'])
def getPendingLeaves():
    return UserService.getPendingLeaves()

@user_bp.route('/location-point', methods=['POST'])
def addLocationPoint():
    return UserService.addLocationPoint()

@user_bp.route('/employee/<int:user_id>/location', methods=['GET'])
def getEmployeeLocations(user_id):
    return UserService.getEmployeeLocations(user_id)

@user_bp.route('/approve-leave', methods=['POST'])
def approveLeave():
    try:
        print("**********************")
        payload = request.get_json()
        return UserService.approveLeave(payload)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Error approving leave"}), 500

@user_bp.route('/add-leave', methods=['POST'])
def addLeave():
    try:
        payload = request.get_json()
        return UserService.addLeave(payload)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while adding leave"
        }), 500

@user_bp.route('/add-break', methods=['POST'])
def addBreak():
    try:
        payload = request.get_json()
        return UserService.addBreak(payload)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while adding break"
        }), 500

@user_bp.route('/end-break', methods=['POST'])
def endBreak():
    try:
        payload = request.get_json()
        return UserService.endBreak(payload)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while ending break"
        }), 500
    
@user_bp.route('/createRole', methods=['POST'])
def createRole():
    return UserService.createRole()

@user_bp.route('/addPermissionsToRole', methods=['POST'])
def addPermissionsToRole():
    return UserService.addPermissionsToRole()

@user_bp.route('/removePermissionsFromRole', methods=['POST'])
def removePermissionsToRole():
    return UserService.removePermissionsToRole()

@user_bp.route('/roles', methods=['GET'])
def getAllRoles():
    return UserService.getRoles()

@user_bp.route('/updateRole/<int:role_id>', methods=['PUT'])
def updateRole(role_id):
    return UserService.getRoleById(role_id)

@user_bp.route('/permissions', methods=['GET'])
def getPermissions():
    return UserService.getPermissions()

@user_bp.route('/updatePermission/<int:permission_id>', methods=['PUT'])
def updatePermission(permission_id):
    return UserService.updatePermission(permission_id)

@user_bp.route('/permissions', methods=['POST'])
def addNewPermission():
    return UserService.addNewPermission()

@user_bp.route('/user', methods=['POST'])
def post():
    return UserService.CreateUser()

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def getUserById(user_id):
    return UserService.getUserById(user_id)

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def updateUser(user_id):
    UserService.updateUser(user_id)
    return UserService.getUser(user_id)

@user_bp.route('/employee-logs-data', methods=['POST'])
def getEmployeeLogsData():
    try:
        payload = request.get_json()
        return UserService.getEmployeeLogsData(payload)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while fetching logs data"
        }), 500
    
@user_bp.route('/report', methods=['POST'])
def generateReport():
    try:
        payload = request.get_json()
        # Delegate PDF creation to UserService
        pdf_buffer = UserService.generateReport(payload)

        # Ensure PDF stream is valid before sending
        if isinstance(pdf_buffer, BytesIO):
            pdf_buffer.seek(0)
            return send_file(
                pdf_buffer,
                as_attachment=False,
                mimetype="application/pdf",
                download_name="employee_report.pdf"
            )
        else:
            return jsonify({"message": "Error generating PDF report"}), 500

    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "An error occurred while generating report"
        }), 500