import salabim as sim

left=-1
right=+1

def sidename(side):
    return 'l' if side==left else 'r'
                     
class Shipgenerator(sim.Component):

    def process(self):
        while True:
            yield self.hold(sim.Exponential(iat).sample())
            ship=Ship(name=sidename(self.side)+'ship.')
            ship.side=self.side
            ship.length=meanlength*sim.Uniform(2/3,4/3).sample()
            if lock.mode()=='Idle':
                lock.activate()
            
class Ship(sim.Component):
    def process(self):
        if lock.ispassive():
            lock.activate()
        yield self.request((lockmeters[self.side],self.length),key_in[self.side])
        self.enter(lockqueue)
        yield self.hold(intime)
        self.release(key_in[self.side])
        yield self.request(key_out)
        yield self.hold(outtime)
        self.leave(lockqueue)
        self.release(key_out)        
                
class Lock(sim.Component):

    def process(self):
        yield self.request(key_in[left])
        yield self.request(key_in[right])
        yield self.request(key_out)
        
        while True:
            if len(key_in[self.side].requesters())==0:
                if len(key_in[-self.side].requesters())==0:
                    yield self.passivate()
            self.release(key_in[self.side])
            yield self.request((key_in[self.side],1,1000))
            lockmeters[self.side].release()
            yield self.hold(switchtime,mode='Switch')
            self.side=-self.side
            self.release(key_out)
            yield self.request((key_out,1,1000),mode=None)
            
de=sim.Environment(random_seed=1234567,trace=False)

locklength=60
switchtime=10
intime=2
outtime=2
meanlength=30
iat=30

lockmeters={}
key_in={}
lockqueue=sim.Queue('lockqueue')    
key_out=sim.Resource(name=' key_out')

for side in (left,right):
    lockmeters[side]=sim.Resource(capacity=locklength,name=sidename(side)+' lock meters',anonymous=True)
    key_in[side]=sim.Resource(name=sidename(side)+' key in')    
    shipgenerator=Shipgenerator(name=sidename(side)+'Shipgenerator')
    shipgenerator.side=side

lock=Lock('Lock')
lock.side=left

de.run(50000)

for side in (left,right):
    lockmeters[side].claimed_quantity.print_histogram(30,0,10)


