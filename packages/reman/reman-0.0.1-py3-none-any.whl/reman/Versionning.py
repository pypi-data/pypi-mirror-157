#!/usr/bin/python3
import mariadb
import sys

class Versionning(object):
	def __init__(self):
		self.connection = None
		self.cursor = None

	def __del__(self):
		if (self.cursor != None):
			self.cursor.close()
		if (self.connection != None):
			self.connection.close()

	def getVersion(self, releaseName, packageName):
		print("getting version for " + packageName + " in " + releaseName)
		result = None
		try:
			cursor = self.getDBCursor()
			cursor.execute(f"SELECT version FROM PackageVersions pkgVers INNER JOIN Releases rels INNER JOIN Packages pkgs INNER JOIN ReleasePackages relPkgs "
				+ f"WHERE relPkgs.releaseId=rels.id AND relPkgs.packageVersionId=pkgVers.id AND pkgVers.packageId=pkgs.id AND rels.name='{releaseName}' AND pkgs.name='{packageName}'")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
			else:
				print("None or multiple version! " + len(rows))
		except Exception as e:
			print(f"Failed to get version of {packageName}, error: {e}")
		print(f"getVersion {result}")
		return result

	def createRelease(self, releaseName):
		self.getDBCursor().execute(f"SELECT id FROM Releases WHERE name='{releaseName}'")
		if (len(self.getDBCursor().fetchall()) > 0):
			print("Release already exists")
			return
		try:
			self.getDBCursor().execute(f"INSERT INTO Releases (name) VALUES ('{releaseName}')")
			self.getDBConnection().commit()
		except Exception as e:
			print(f"Failed to create release {releaseName}, error: {e}")
			sys.exit(1)

	def createPackage(self, packageName):
		self.getDBCursor().execute(f"SELECT id FROM Packages WHERE name='{packageName}'")
		if (len(self.getDBCursor().fetchall()) > 0):
			print("Package already exists")
			return
		try:
			self.getDBCursor().execute(f"INSERT INTO Packages (name) VALUES ('{packageName}')")
			self.getDBConnection().commit()
		except Exception as e:
			print(f"Failed to create package {packageName}, error: {e}")
			sys.exit(1)

	def createVersion(self, releaseName, packageName, version, sourcePath=None):
		packageId = self.getPackageId(packageName)
		self.getDBCursor().execute(f"SELECT id FROM PackageVersions WHERE packageId={packageId} AND version='{version}'")
		if (len(self.getDBCursor().fetchall()) > 0):
			print("Version already exists")
			return
		sourcePath = "http://"
		try:
			self.getDBCursor().execute(f"INSERT INTO PackageVersions (packageId, version, sourcePath) VALUES ({packageId}, '{version}', '{sourcePath}')")
			self.getDBConnection().commit()
		except Exception as e:
			print(f"Failed to create version for {packageName} in {releaseName}, error: {e}")
			#sys.exit(1)
		packageVersionId = self.getPackageVersionId(packageId, version)
		releaseId = self.getReleaseId(releaseName)
		if (packageVersionId == None):
			print("package version id not found")
			sys.exit(1)
		if (self.getVersion(releaseName, packageName) == None):
			try:
				self.getDBCursor().execute(f"INSERT INTO ReleasePackages (releaseId, packageId, packageVersionId) VALUES ('{releaseId}', {packageId}, {packageVersionId})")
				self.getDBConnection().commit()
			except Exception as e:
				print(f"Failed to insert version for release, error: {e}")
		else:
			try:
				self.getDBCursor().execute(f"UPDATE ReleasePackages set packageVersionId={packageVersionId} WHERE releaseId={releaseId} AND packageId={packageId}")
				self.getDBConnection().commit()
			except Exception as e:
				print(f"Failed to update version of {packageName} for release, error: {e}")


	def getPackageId(self, packageName):
		try:
			self.getDBCursor().execute(f"SELECT id FROM Packages WHERE name='{packageName}'")
			row = self.getDBCursor().fetchone()
			return row[0]
		except Exception as e:
			print(f"Failed to get package id {packageName}, error: {e}")
			sys.exit(1)

	def getPackageVersionId(self, packageId, version):
		try:
			result = None
			self.getDBCursor().execute(f"SELECT id FROM PackageVersions WHERE packageId={packageId} AND version='{version}'")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get package version id, error: {e}")
		return result

	def getPackageIdInRelease(self, releaseId, packageId):
		try:
			result = None
			self.getDBCursor().execute(f"SELECT packageVersionId FROM ReleasePackages WHERE packageId={packageId} AND releaseId='{releaseId}'")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get package version id, error: {e}")
		return result

	def getReleaseId(self, releaseName):
		try:
			result = None
			self.getDBCursor().execute(f"SELECT id FROM Releases WHERE name='{releaseName}'")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get release id, error: {e}")
		return result

	def getSourcePath(self, releaseName, packageName):
		result = None
		releaseId = self.getReleaseId(releaseName)
		packageId = self.getPackageId(packageName)
		packageVersionId = self.getPackageIdInRelease(releaseId, packageId)
		try:
			self.getDBCursor().execute(f"SELECT sourcePath FROM PackageVersions WHERE id='{packageVersionId}'")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get release id, error: {e}")
		return result

	def getUser(self, releaseName, packageName):
		result = None
		releaseId = self.getReleaseId(releaseName)
		packageId = self.getPackageId(packageName)
		try:
			self.getDBCursor().execute("SELECT name FROM Users users INNER JOIN ReleaseUserChannel ruc "
				+ f"WHERE ruc.userId = users.id AND ruc.releaseId = {self.getReleaseId(releaseName)} AND ruc.packageId = {self.getPackageId(packageName)}")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get release id, error: {e}")
		return result


	def getChannel(self, releaseName, packageName):
		result = None
		releaseId = self.getReleaseId(releaseName)
		packageId = self.getPackageId(packageName)
		try:
			self.getDBCursor().execute("SELECT name FROM Channels channels INNER JOIN ReleaseUserChannel ruc "
				+ f"WHERE ruc.userId = channels.id AND ruc.releaseId = {self.getReleaseId(releaseName)} AND ruc.packageId = {self.getPackageId(packageName)}")
			rows = self.getDBCursor().fetchall()
			if (len(rows) == 1):
				result = rows[0][0]
		except Exception as e:
			print(f"Failed to get release id, error: {e}")
		return result

		

	def getDBConnection(self):
		try:
			if (self.connection == None):
				self.connection = mariadb.connect(
					user="sdenys",
					password="sdenys",
					host="127.0.0.1",
					database="package-versionning")
			return self.connection
		except Exception as e:
			print(f"Failed to connect database, error: {e}")
			sys.exit(1)

	def getDBCursor(self):
		try:
			if (self.cursor == None):
				self.cursor = self.getDBConnection().cursor()
			return self.cursor
		except Exception as e:
			print(f"Failed to get database cursor, error: {e}")
			sys.exit(1)
	def runStatement():
		pass