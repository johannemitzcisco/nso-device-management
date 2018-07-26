# -*- mode: python; python-indent: 4 -*-
import ncs
import subprocess
import os, sys
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
    from subprocess32 import CalledProcessError
else:
    import subprocess
    from subprocess import CalledProcessError

class DeviceManagement:
    netsim = os.environ["NCS_DIR"]+"/bin/ncs-netsim"

    def nso_register(self, log, root, service, name, address, port, authgroup, devicetype, nedid):
        log.info("Registering device with NSO: ", name, "(", nedid, ")")
        if devicetype == 'netconf':
            nedid = 'netconf'
        log.info("Adding device: ", name)
        log.info("Address: ", address)
        log.info("Port: ", port)
        log.info("Authgroup: ", authgroup)
        log.info("Device Type: ", devicetype)
        log.info("NED ID: ", nedid)

        vars = ncs.template.Variables()
        vars.add('DEVICE-NAME', name)
        vars.add('ADDRESS', address)
        vars.add('PORT', port)
        vars.add('AUTHGROUP', authgroup)
        vars.add('DEVICE-TYPE', devicetype)
        vars.add('NED-ID', nedid)
        template = ncs.template.Template(service)
        template.apply('nso-device-template', vars)
        log.info("Device Registered with NSO: ", name, "(", nedid, ")")
        device = ncs.maagic.cd(root.devices.device, name)
        device.ssh.fetch_host_keys()
        device.sync_from()

    def netsim_create(self, log, service, name, nedid):
        log.info("Creating netsim device: ", name, "(", nedid, ")")
        try:
            subprocess.check_output([self.netsim, "add-device", nedid, name])
            log.info("Device added to NetSim")
        except CalledProcessError as cpe:
            log.info("Error adding netsim device, attempting to create NetSim device instead: ", name)
            try:
                subprocess.check_output([self.netsim, "create-device", nedid, name])
                log.info("Device created in NetSim")
            except CalledProcessError as cpe:
                log.info("Unable to create netsim device: ", name)

    def netsim_start(self, log, devicename=None):
        if devicename is None:
            try:
                log.info("Starting all NetSim devices")
                subprocess.check_output([self.netsim, "start"])
                log.info("NetSim network started")
            except CalledProcessError as cpe:
                log.info("Unable to start netsim network")
        else:
            try:
                log.info("Starting NetSim device: ", devicename)
                subprocess.check_output([self.netsim, "start", devicename])
                log.info("NetSim device started", devicename)
            except CalledProcessError as cpe:
                log.info("Unable to start netsim device: ", devicename)

    def netsim_delete(self, log):
        try:
            log.info("Removing all NetSim devices")
            subprocess.check_output([self.netsim, "delete-network"])
            log.info("NetSim network deleted")
        except CalledProcessError as cpe:
            log.info("Unable to delete netsim network")



# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
# class ServiceCallbacks(Service):

#     # The create() callback is invoked inside NCS FASTMAP and
#     # must always exist.
#     @Service.create
#     def cb_create(self, tctx, root, service, proplist):
#         self.log.info('Service create(service=', service._path, ')')

#         vars = ncs.template.Variables()
#         vars.add('DUMMY', '127.0.0.1')
#         template = ncs.template.Template(service)
#         template.apply('nso-device-management-template', vars)

#     # The pre_modification() and post_modification() callbacks are optional,
#     # and are invoked outside FASTMAP. pre_modification() is invoked before
#     # create, update, or delete of the service, as indicated by the enum
#     # ncs_service_operation op parameter. Conversely
#     # post_modification() is invoked after create, update, or delete
#     # of the service. These functions can be useful e.g. for
#     # allocations that should be stored and existing also when the
#     # service instance is removed.

#     # @Service.pre_lock_create
#     # def cb_pre_lock_create(self, tctx, root, service, proplist):
#     #     self.log.info('Service plcreate(service=', service._path, ')')

#     # @Service.pre_modification
#     # def cb_pre_modification(self, tctx, op, kp, root, proplist):
#     #     self.log.info('Service premod(service=', kp, ')')

#     # @Service.post_modification
#     # def cb_post_modification(self, tctx, op, kp, root, proplist):
#     #     self.log.info('Service premod(service=', kp, ')')


# # ---------------------------------------------
# # COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# # ---------------------------------------------
# class Main(ncs.application.Application):
#     def setup(self):
#         # The application class sets up logging for us. It is accessible
#         # through 'self.log' and is a ncs.log.Log instance.
#         self.log.info('DeviceManagement RUNNING')

#         # Service callbacks require a registration for a 'service point',
#         # as specified in the corresponding data model.
#         #
#         #self.register_service('nso-device-management-servicepoint', ServiceCallbacks)

#         # If we registered any callback(s) above, the Application class
#         # took care of creating a daemon (related to the service/action point).

#         # When this setup method is finished, all registrations are
#         # considered done and the application is 'started'.

#     def teardown(self):
#         # When the application is finished (which would happen if NCS went
#         # down, packages were reloaded or some error occurred) this teardown
#         # method will be called.

#         self.log.info('DeviceManagement FINISHED')
