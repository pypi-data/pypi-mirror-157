
from nyto import particle
import numpy as np
from nyto import unit_function as uf

class layer(particle.particle):
	def __repr__(self):
		class_name=self.__class__.__name__
		if self.is_fix:
			return f"{class_name}({self.shape}, Fix={self.is_fix})"
		return f"{class_name}({self.shape})"

class variable_layer(layer):
	'''
	[mod]
	(np)values: tag(variable)
	'''
	def __getitem__(self, key):
		return self.values[key]
	
	@property
	def shape(self):
		return self.values.shape
	
	@property
	def values(self):
		return self.mod['values']

	@values.setter
	def values(self, new_var):
		self.mod['values']=new_var

class nn_layer(layer):
	'''
	[mod]
	(np)weights: tag(weights, dropout)
	(np)bias:    tag(bias)
	'''

	def __call__(self, input_data):
		if type(input_data)==np.ndarray:
			return_np=input_data.dot(self.weights)+self.bias
			return return_np

		if type(input_data)==variable_layer:
			return self(input_data.values)

		raise ValueError("input data type is not correct!")
	
	@property
	def shape(self):
		return self.weights.shape

	@property
	def weights(self):
		return self.mod['weights']

	@weights.setter
	def weights(self, new_weights):
		self.mod['weights'] = new_weights

	@property
	def bias(self):
		return self.mod['bias']

	@bias.setter
	def bias(self, new_bias):
		self.mod['bias'] = new_bias

class lstm_layer(layer):
    '''
    [mod]
        (variable_layer)com_in:       tag(weights, dropout)
        (variable_layer)com_mem:      tag(weights, dropout)
        (variable_layer)com_out:      tag(weights, dropout)
        (variable_layer)com_bias:     tag(bias)

        (variable_layer)ingate_in:    tag(weights, dropout)
        (variable_layer)ingate_mem:   tag(weights, dropout)
        (variable_layer)ingate_out:   tag(weights, dropout)
        (variable_layer)ingate_bias:  tag(bias)

        (variable_layer)outgate_in:   tag(weights, dropout)
        (variable_layer)outgate_mem:  tag(weights, dropout)
        (variable_layer)outgate_out:  tag(weights, dropout)
        (variable_layer)outgate_bias: tag(bias)

        (variable_layer)forgate_in:   tag(weights, dropout)
        (variable_layer)forgate_mem:  tag(weights, dropout)
        (variable_layer)forgate_out:  tag(weights, dropout)
        (variable_layer)forgate_bias: tag(bias)

        (variable_layer)init_mem:     tag(init_state)
        (variable_layer)init_out:     tag(init_state)
    [var]
        (def)com_func:                _tanh
        (def)ingate_func:             _sigmoid
        (def)outgate_func:            _sigmoid
        (def)forgate_func:            _sigmoid
        (def)final_func:              _tanh
    '''

    def _neural_compute(self, in_v, mem_v, out_v, in_w, mem_w, out_w, bias):
        return in_v.dot(in_w.values)+mem_v.dot(mem_w.values)+out_v.dot(out_w.values)+bias.values

    def run(self, in_np, mem_np, out_np):
        com_ret=self.com_func(self._neural_compute(
            in_np, mem_np, out_np,
            self.com_in, self.com_mem, self.com_out, self.com_bias
        ))

        ingate_ret=self.ingate_func(self._neural_compute(
            in_np, mem_np, out_np,
            self.ingate_in, self.ingate_mem, self.ingate_out, self.ingate_bias
        ))

        outgate_ret=self.outgate_func(self._neural_compute(
            in_np, mem_np, out_np,
            self.outgate_in, self.outgate_mem, self.outgate_out, self.outgate_bias
        ))

        forgate_ret=self.forgate_func(self._neural_compute(
            in_np, mem_np, out_np,
            self.forgate_in, self.forgate_mem, self.forgate_out, self.forgate_bias
        ))

        new_mem=com_ret*ingate_ret+mem_np*forgate_ret
        final_ret=self.final_func(new_mem)*outgate_ret

        return final_ret, new_mem

    def run_series(self, input_data):
        return_data_list=[]
        last_output=self.init_out.values
        memory_np=self.init_mem.values
        for this_times_data_np in input_data:
            this_times_data_np=this_times_data_np[np.newaxis,:]
            last_output, memory_np=self.run(
                this_times_data_np, memory_np, last_output
            )
            return_data_list.append(last_output.squeeze(0))

        return np.array(return_data_list)

    def __call__(self, batch_data):
        return [self.run_series(data) for data in batch_data]

    @property
    def shape(self):
        return self.com_in.shape

    @property
    def com_in(self): return self.mod['com_in']
    @property
    def com_mem(self): return self.mod['com_mem']
    @property
    def com_out(self): return self.mod['com_out']
    @property
    def com_bias(self): return self.mod['com_bias']

    @com_in.setter
    def com_in(self,x): self.mod['com_in']=x
    @com_mem.setter
    def com_mem(self,x): self.mod['com_mem']=x
    @com_out.setter
    def com_out(self,x): self.mod['com_out']=x
    @com_bias.setter
    def com_bias(self,x): self.mod['com_bias']=x
    
    @property
    def ingate_in(self): return self.mod['ingate_in']
    @property
    def ingate_mem(self): return self.mod['ingate_mem']
    @property
    def ingate_out(self): return self.mod['ingate_out']
    @property
    def ingate_bias(self): return self.mod['ingate_bias']

    @ingate_in.setter
    def ingate_in(self,x): self.mod['ingate_in']=x
    @ingate_mem.setter
    def ingate_mem(self,x): self.mod['ingate_mem']=x
    @ingate_out.setter
    def ingate_out(self,x): self.mod['ingate_out']=x
    @ingate_bias.setter
    def ingate_bias(self,x): self.mod['ingate_bias']=x
    
    @property
    def outgate_in(self): return self.mod['outgate_in']
    @property
    def outgate_mem(self): return self.mod['outgate_mem']
    @property
    def outgate_out(self): return self.mod['outgate_out']
    @property
    def outgate_bias(self): return self.mod['outgate_bias']

    @outgate_in.setter
    def outgate_in(self,x): self.mod['outgate_in']=x
    @outgate_mem.setter
    def outgate_mem(self,x): self.mod['outgate_mem']=x
    @outgate_out.setter
    def outgate_out(self,x): self.mod['outgate_out']=x
    @outgate_bias.setter
    def outgate_bias(self,x): self.mod['outgate_bias']=x
    
    @property
    def forgate_in(self): return self.mod['forgate_in']
    @property
    def forgate_mem(self): return self.mod['forgate_mem']
    @property
    def forgate_out(self): return self.mod['forgate_out']
    @property
    def forgate_bias(self): return self.mod['forgate_bias']

    @forgate_in.setter
    def forgate_in(self,x): self.mod['forgate_in']=x
    @forgate_mem.setter
    def forgate_mem(self,x): self.mod['forgate_mem']=x
    @forgate_out.setter
    def forgate_out(self,x): self.mod['forgate_out']=x
    @forgate_bias.setter
    def forgate_bias(self,x): self.mod['forgate_bias']=x
    
    @property
    def init_mem(self): return self.mod['init_mem']
    @property
    def init_out(self): return self.mod['init_out']

    @init_mem.setter
    def init_mem(self,x): self.mod['init_mem']=x
    @init_out.setter
    def init_out(self,x): self.mod['init_out']=x
    
    @property
    def com_func(self): return self.mod['com_func']
    @property
    def ingate_func(self): return self.mod['ingate_func']
    @property
    def outgate_func(self): return self.mod['outgate_func']
    @property
    def forgate_func(self): return self.mod['forgate_func']
    @property
    def final_func(self): return self.mod['final_func']

    @com_func.setter
    def com_func(self,x): self.mod['com_func']=x
    @ingate_func.setter
    def ingate_func(self,x): self.mod['ingate_func']=x
    @outgate_func.setter
    def outgate_func(self,x): self.mod['outgate_func']=x
    @forgate_func.setter
    def forgate_func(self,x): self.mod['forgate_func']=x
    @final_func.setter
    def final_func(self,x): self.mod['final_func']=x

class conv_layer(layer):
	'''
	[mod]
		(np)filter_np: tag(weights, convolution)
		(np)filter_np: 4d_np[filter_shape, img_shape, row_split, col_split]
	[var]
		(def)conv_func: _convolution
		(str)pad_mod:   'full' or 'valid' or 'same'
		(int)strides:   窗口移動間隔
	'''

	def __call__(self, data_4d_np):
		return self.conv_func(
			data_np=data_4d_np,
			filter_np=self.filter_np,
			mod=self.pad_mod,
			strides=self.strides
		)
	
	@property
	def shape(self):
		(filter_shape, img_shape, row_split, col_split)=self.filter_np.shape
		return (img_shape, filter_shape), (row_split, col_split)
	
	@property
	def filter_np(self): return self.mod['filter_np']
	@filter_np.setter
	def filter_np(self, x): self.mod['filter_np']=x

	@property
	def conv_func(self): return self.var_dict['_convolution']
	@conv_func.setter
	def conv_func(self, x): self.var_dict['_convolution']=x

	@property
	def pad_mod(self): return self.var_dict['pad_mod']
	@pad_mod.setter
	def pad_mod(self, x): self.var_dict['pad_mod']=x

	@property
	def strides(self): return self.var_dict['strides']
	@strides.setter
	def strides(self, x): self.var_dict['strides']=x

def new_variable_layer(
	structure, init_values=0, random_size=None, dropout=False, fix=False,
	tags={'variable'}
):
	new_variable = variable_layer()
	if random_size is None:
		new_variable.values=np.zeros(structure)+init_values
		if dropout: new_variable.tag['dropout']={'values'}
		for tag in tags: new_variable.tag[tag]={'values'}
		return new_variable

	new_variable.values=np.random.standard_normal(size=structure)*random_size
	new_variable.values+=init_values
	if dropout: new_variable.tag['dropout']={'values'}
	for tag in tags: new_variable.tag['variable']={'values'}
	
	if fix: new_variable.fix()
	return new_variable

def np_to_variable_layer(variable_np, dropout=False, fix=False, tags={'variable'}):
	new_variable = variable_layer()
	new_variable.values=variable_np
	if dropout: new_variable.tag['dropout']={'values'}
	for tag in tags: new_variable.tag[tag]={'values'}
	
	if fix: new_variable.fix()
	return new_variable

def new_nn_layer(
	structure, init_values=(0,0), random_size=(None,None), dropout=True, fix=False
):
	new_nn = nn_layer()

	if random_size[0] is None:
		new_nn.weights=np.zeros(structure)+init_values[0]
	else:
		new_nn.weights=np.random.standard_normal(size=structure)*random_size[0]
		new_nn.weights+=init_values[0]

	if random_size[1] is None:
		new_nn.bias=np.zeros((1,structure[1]))+init_values[1]
	else:
		new_nn.bias=np.random.normal(size=(1,structure[1]))*random_size[1]
		new_nn.bias+=init_values[1]

	if dropout: new_nn.tag['dropout'] = {'weights'}
	new_nn.tag['weights'] = {'weights'}
	new_nn.tag['bias'] = {'bias'}
	
	if fix: new_nn.fix()
	return new_nn

def _new_lstm_layer(
    structure,

    com_in_init=0, com_in_random=None, com_in_dropout=True, com_in_fix=False,
    com_mem_init=0, com_mem_random=None, com_mem_dropout=True, com_mem_fix=False,
    com_out_init=0, com_out_random=None, com_out_dropout=True, com_out_fix=False,
    com_bias_init=0, com_bias_random=None, com_bias_dropout=False, com_bias_fix=False,

    ingate_in_init=0, ingate_in_random=None, ingate_in_dropout=True, ingate_in_fix=False,
    ingate_mem_init=0, ingate_mem_random=None, ingate_mem_dropout=True, ingate_mem_fix=False,
    ingate_out_init=0, ingate_out_random=None, ingate_out_dropout=True, ingate_out_fix=False,
    ingate_bias_init=0, ingate_bias_random=None, ingate_bias_dropout=False, ingate_bias_fix=False,

    outgate_in_init=0, outgate_in_random=None, outgate_in_dropout=True, outgate_in_fix=False,
    outgate_mem_init=0, outgate_mem_random=None, outgate_mem_dropout=True, outgate_mem_fix=False,
    outgate_out_init=0, outgate_out_random=None, outgate_out_dropout=True, outgate_out_fix=False,
    outgate_bias_init=0, outgate_bias_random=None, outgate_bias_dropout=False, outgate_bias_fix=False,

    forgate_in_init=0, forgate_in_random=None, forgate_in_dropout=True, forgate_in_fix=False,
    forgate_mem_init=0, forgate_mem_random=None, forgate_mem_dropout=True, forgate_mem_fix=False,
    forgate_out_init=0, forgate_out_random=None, forgate_out_dropout=True, forgate_out_fix=False,
    forgate_bias_init=0, forgate_bias_random=None, forgate_bias_dropout=False, forgate_bias_fix=False,

    init_mem_init=0, init_mem_random=None, init_mem_dropout=False, init_mem_fix=False,
    init_out_init=0, init_out_random=None, init_out_dropout=False, init_out_fix=False,

    com_func=uf._tanh,
    ingate_func=uf._sigmoid,
    outgate_func=uf._sigmoid,
    forgate_func=uf._sigmoid,
    final_func=uf._tanh
):

    return_lstm=lstm_layer()
    (input_size, output_size)=structure

    return_lstm.com_in=new_variable_layer(
        (input_size,output_size), init_values=com_in_init, random_size=com_in_random,
        dropout=com_in_dropout, fix=com_in_fix, tags={'weights'}
    )
    return_lstm.com_mem=new_variable_layer(
        (output_size,output_size), init_values=com_mem_init, random_size=com_mem_random,
        dropout=com_mem_dropout, fix=com_mem_fix, tags={'weights'}
    )
    return_lstm.com_out=new_variable_layer(
        (output_size,output_size), init_values=com_out_init, random_size=com_out_random,
        dropout=com_out_dropout, fix=com_out_fix, tags={'weights'}
    )
    return_lstm.com_bias=new_variable_layer(
        (1,output_size), init_values=com_bias_init, random_size=com_bias_random,
        dropout=com_bias_dropout, fix=com_bias_fix, tags={'bias'}
    )

    return_lstm.ingate_in=new_variable_layer(
        (input_size,output_size), init_values=ingate_in_init, random_size=ingate_in_random,
        dropout=ingate_in_dropout, fix=ingate_in_fix, tags={'weights'}
    )
    return_lstm.ingate_mem=new_variable_layer(
        (output_size,output_size), init_values=ingate_mem_init, random_size=ingate_mem_random,
        dropout=ingate_mem_dropout, fix=ingate_mem_fix, tags={'weights'}
    )
    return_lstm.ingate_out=new_variable_layer(
        (output_size,output_size), init_values=ingate_out_init, random_size=ingate_out_random,
        dropout=ingate_out_dropout, fix=ingate_out_fix, tags={'weights'}
    )
    return_lstm.ingate_bias=new_variable_layer(
        (1,output_size), init_values=ingate_bias_init, random_size=ingate_bias_random,
        dropout=ingate_bias_dropout, fix=ingate_bias_fix, tags={'bias'}
    )

    return_lstm.outgate_in=new_variable_layer(
        (input_size,output_size), init_values=outgate_in_init, random_size=outgate_in_random,
        dropout=outgate_in_dropout, fix=outgate_in_fix, tags={'weights'}
    )
    return_lstm.outgate_mem=new_variable_layer(
        (output_size,output_size), init_values=outgate_mem_init, random_size=outgate_mem_random,
        dropout=outgate_mem_dropout, fix=outgate_mem_fix, tags={'weights'}
    )
    return_lstm.outgate_out=new_variable_layer(
        (output_size,output_size), init_values=outgate_out_init, random_size=outgate_out_random,
        dropout=outgate_out_dropout, fix=outgate_out_fix, tags={'weights'}
    )
    return_lstm.outgate_bias=new_variable_layer(
        (1,output_size), init_values=outgate_bias_init, random_size=outgate_bias_random,
        dropout=outgate_bias_dropout, fix=outgate_bias_fix, tags={'bias'}
    )

    return_lstm.forgate_in=new_variable_layer(
        (input_size,output_size), init_values=forgate_in_init, random_size=forgate_in_random,
        dropout=forgate_in_dropout, fix=forgate_in_fix, tags={'weights'}
    )
    return_lstm.forgate_mem=new_variable_layer(
        (output_size,output_size), init_values=forgate_mem_init, random_size=forgate_mem_random,
        dropout=forgate_mem_dropout, fix=forgate_mem_fix, tags={'weights'}
    )
    return_lstm.forgate_out=new_variable_layer(
        (output_size,output_size), init_values=forgate_out_init, random_size=forgate_out_random,
        dropout=forgate_out_dropout, fix=forgate_out_fix, tags={'weights'}
    )
    return_lstm.forgate_bias=new_variable_layer(
        (1,output_size), init_values=forgate_bias_init, random_size=forgate_bias_random,
        dropout=forgate_bias_dropout, fix=forgate_bias_fix, tags={'bias'}
    )

    return_lstm.init_mem=new_variable_layer(
        (1,output_size), init_values=init_mem_init, random_size=init_mem_random,
        dropout=init_mem_dropout, fix=init_mem_fix, tags={'init_state'}
    )
    return_lstm.init_out=new_variable_layer(
        (1,output_size), init_values=init_out_init, random_size=init_out_random,
        dropout=init_out_dropout, fix=init_out_fix, tags={'init_state'}
    )

    return_lstm.com_func=com_func
    return_lstm.ingate_func=ingate_func
    return_lstm.outgate_func=outgate_func
    return_lstm.forgate_func=forgate_func
    return_lstm.final_func=final_func

    return return_lstm

def new_lstm_layer(
    structure,
    compute_init=(0,0), compute_random=(None,None),
    input_init=(0,0), input_random=(None,None),
    output_init=(0,0), output_random=(None,None),
    forget_init=(0,0), forget_random=(None,None),
    state_init=0, state_random=None,
    input_data_dropout=True,
    mem_data_dropout=False,
    reinput_data_dropout=False,
    com_func=uf._tanh,
    ingate_func=uf._sigmoid,
    outgate_func=uf._sigmoid,
    forgate_func=uf._sigmoid,
    final_func=uf._tanh,
    fix=False
):

    (com_wi, com_bi)=compute_init
    (com_wr, com_br)=compute_random
    (in_wi, in_bi)=input_init
    (in_wr, in_br)=input_random
    (out_wi, out_bi)=output_init
    (out_wr, out_br)=output_random
    (for_wi, for_bi)=forget_init
    (for_wr, for_br)=forget_random

    (in_dr,mem_dr,out_dr)=(input_data_dropout,mem_data_dropout,reinput_data_dropout)

    ret_lstm=_new_lstm_layer(
        structure=structure,

        com_in_init=com_wi, com_in_random=com_wr, com_in_dropout=in_dr, com_in_fix=False,
        com_mem_init=com_wi, com_mem_random=com_wr, com_mem_dropout=mem_dr, com_mem_fix=False,
        com_out_init=com_wi, com_out_random=com_wr, com_out_dropout=out_dr, com_out_fix=False,
        com_bias_init=com_bi, com_bias_random=com_br, com_bias_dropout=False, com_bias_fix=False,

        ingate_in_init=in_wi, ingate_in_random=in_wr, ingate_in_dropout=in_dr, ingate_in_fix=False,
        ingate_mem_init=in_wi, ingate_mem_random=in_wr, ingate_mem_dropout=mem_dr, ingate_mem_fix=False,
        ingate_out_init=in_wi, ingate_out_random=in_wr, ingate_out_dropout=out_dr, ingate_out_fix=False,
        ingate_bias_init=in_bi, ingate_bias_random=in_br, ingate_bias_dropout=False, ingate_bias_fix=False,

        outgate_in_init=out_wi, outgate_in_random=out_wr, outgate_in_dropout=in_dr, outgate_in_fix=False,
        outgate_mem_init=out_wi, outgate_mem_random=out_wr, outgate_mem_dropout=mem_dr, outgate_mem_fix=False,
        outgate_out_init=out_wi, outgate_out_random=out_wr, outgate_out_dropout=out_dr, outgate_out_fix=False,
        outgate_bias_init=out_bi, outgate_bias_random=out_br, outgate_bias_dropout=False, outgate_bias_fix=False,

        forgate_in_init=for_wi, forgate_in_random=for_wr, forgate_in_dropout=in_dr, forgate_in_fix=False,
        forgate_mem_init=for_wi, forgate_mem_random=for_wr, forgate_mem_dropout=mem_dr, forgate_mem_fix=False,
        forgate_out_init=for_wi, forgate_out_random=for_wr, forgate_out_dropout=out_dr, forgate_out_fix=False,
        forgate_bias_init=for_bi, forgate_bias_random=for_br, forgate_bias_dropout=False, forgate_bias_fix=False,

        init_mem_init=state_init, init_mem_random=state_random, init_mem_dropout=False, init_mem_fix=False,
        init_out_init=state_init, init_out_random=state_random, init_out_dropout=False, init_out_fix=False,

        com_func=com_func,
        ingate_func=ingate_func,
        outgate_func=outgate_func,
        forgate_func=forgate_func,
        final_func=final_func
    )

    if fix: ret_lstm.fix()
    return ret_lstm

def new_conv_layer(
	structure, kernal_size=(3,3),
	init_values=0, random_size=None, dropout=False,
	pad_mod='valid', strides=1,
	fix=False
):
	(input_size,output_size)=structure
	filter_shape=(output_size,input_size,*kernal_size)
	
	new_conv = conv_layer()
	new_conv.conv_func=uf._convolution
	new_conv.pad_mod=pad_mod
	new_conv.strides=strides

	if random_size is None:
		new_conv.filter_np=np.zeros(filter_shape)+init_values
		if dropout: new_conv.tag['dropout']={'filter_np'}
		new_conv.tag['weights']={'filter_np'}
		new_conv.tag['convolution']={'filter_np'}
		
		if fix: new_conv.fix()
		return new_conv

	new_conv.filter_np=np.random.standard_normal(size=filter_shape)*random_size
	new_conv.filter_np+=init_values
	if dropout: new_conv.tag['dropout']={'filter_np'}
	new_conv.tag['weights']={'filter_np'}
	new_conv.tag['convolution']={'filter_np'}
	
	if fix: new_conv.fix()
	return new_conv
	