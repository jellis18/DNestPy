from Model import *
from Level import *

class Options:
	"""
	DNest Options
	"""
	def __init__(self, numParticles=1, newLevelInterval=10000,\
			maxNumLevels=100,saveInterval=10000, lamb=10.0,\
			beta=10.0, deleteParticles=True, maxNumSaves=np.inf):
		self.numParticles = numParticles
		self.newLevelInterval = newLevelInterval
		self.maxNumLevels = maxNumLevels
		self.saveInterval = saveInterval
		self.lamb = lamb
		self.beta = beta
		self.deleteParticles = deleteParticles
		self.maxNumSaves = maxNumSaves

	def load(self, filename="OPTIONS"):
		opts = np.loadtxt(filename, dtype=int)
		self.numParticles = opts[0]
		self.newLevelInterval = opts[1]
		self.maxNumLevels = opts[2]
		self.lamb = float(opts[3])
		self.beta = float(opts[4])
		self.deleteParticles = bool(opts[5])
		self.maxNumSaves = opts[6]
		if self.maxNumSaves == 0:
			self.maxNumSaves = np.inf

class Sampler:
	"""
	A single DNest sampler.
	"""
	def __init__(self, ModelType, options=Options(), levelsFile=None):
		"""
		Input: The class to be used
		Optional: `options`: Options object
		`levelsFile`: Filename to load pre-made levels from
		"""
		self.options = options
		self.models = [ModelType()\
				for i in xrange(0, options.numParticles)]
		self.indices = [0 for i in xrange(0, options.numParticles)]
		self.levels = LevelSet(levelsFile)

	def run(self):
		"""
		Initialise the models from the prior, and then run the sampler!
		"""
		for which in xrange(0, self.options.numParticles):
			self.models[which].fromPrior()

	#	while True:
	#		self.step()

	def step(self, numSteps=1):
		"""
		Take numSteps steps of the sampler. default=1
		"""
		for i in xrange(0, numSteps):
			which = rng.randint(self.options.numParticles)

			if rng.rand() <= 0.5:
				self.updateIndex(which)
				self.updateModel(which)
			else:
				self.updateModel(which)
				self.updateIndex(which)

	def updateModel(self, which):
		"""
		Move a particle
		"""
		[self.models[which], accepted] = self.models[which]\
			.update(self.levels[self.indices[which]])

	def updateIndex(self, which):
		"""
		Move which particle a level is in
		"""
		delta = np.round(10.0**(2.0*rng.rand())*rng.randn())\
				.astype(int)
		if delta == 0:
			delta = 2*rng.randint(2) - 1
		proposed = self.indices[which] + delta
		if proposed < 0 or proposed >= len(self.levels):
			return

		# Acceptance probability
		logAlpha = self.levels[indices[which]].logX\
			- self.levels[proposed].logX \
			+ self.logPush(proposed) - self.logPush(indices[which])
		if logAlpha > 0.0:
			logAlpha = 0.0

		if rng.rand() <= np.exp(logAlpha):
			self.indices[which] = proposed

	def updateVisits(self, which):
		"""
		Update visits/exceeds level statistics
		and logLKeep
		"""
		if self.models[which].logL > self.levels[-1].logL\
			and len(self.levels) < self.options.maxNumLevels:
			self.logLKeep.append(self.models[which].logL)

		index = self.indices[which]
		if index < len(self.levels) - 1:
			self.levels[index].visits += 1
			if self.models[which].logL > self.levels[index+1].logL:
				self.levels[index].exceeds += 1
		
	def logPush(self, index):
		"""
		Calculate the relative weighting of levels,
		for acceptance probability for Sampler.updateIndex()
		"""
		assert index >= 0 and index < len(self.levels)
		result = 0.0
		if len(self.levels) < self.options.maxNumLevels:
			result += float(index)/self.options.lamb
		return result

if __name__ == '__main__':
	options = Options()
	options.load("OPTIONS")
	print options

