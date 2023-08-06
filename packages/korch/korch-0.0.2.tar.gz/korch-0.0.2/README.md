# Korch
> Simple tools to provide a Keras-like interface to PyTorch.


## Install

`pip install korch`

## Example of usage

We can perform a very simple example using the Fashion MNIST dataset (as is done in the official [PyTorch docs](https://pytorch.org/tutorials/beginner/introyt/trainingyt.html).

```
transform = transforms.Compose(
    [transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))])

# Create datasets for training & validation, download if necessary
training_set = torchvision.datasets.FashionMNIST('./data', train=True, transform=transform, download=True)
validation_set = torchvision.datasets.FashionMNIST('./data', train=False, transform=transform, download=True)

# Create data loaders for our datasets; shuffle for training, not for validation
training_loader = torch.utils.data.DataLoader(training_set, batch_size=4, shuffle=True, num_workers=2)
validation_loader = torch.utils.data.DataLoader(validation_set, batch_size=4, shuffle=False, num_workers=2)
```

See that the only different with respect to basic PyTorch is that we're inhereting from our custom `Module`, not from PyTorch's `nn.Module`:

```
class SimpleModel(Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
```

Following the usual Keras way, we instantiate the model and compile it, providing the *loss* and the *optimizer*. *Metrics* can be provided as well, and are expected as `torchvision.MetricCollection`:

```
model = SimpleModel()
model.compile(loss=torch.nn.CrossEntropyLoss(),
              optimizer=torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9),
              metrics = MetricCollection([Accuracy()]))
```

```
model
```




    SimpleModel(
      (conv1): Conv2d(1, 6, kernel_size=(5, 5), stride=(1, 1))
      (pool): MaxPool2d(kernel_size=2, stride=2, padding=0, dilation=1, ceil_mode=False)
      (conv2): Conv2d(6, 16, kernel_size=(5, 5), stride=(1, 1))
      (fc1): Linear(in_features=256, out_features=120, bias=True)
      (fc2): Linear(in_features=120, out_features=84, bias=True)
      (fc3): Linear(in_features=84, out_features=10, bias=True)
      (loss_fn): CrossEntropyLoss()
    )



```
model.evaluate(training_loader), model.evaluate(validation_loader)
```




    (2.3070596095879874, 2.307082461261749)



```
model.fit(trainloader=training_loader, epochs=1, validationloader=validation_loader)
```

```
model.evaluate(training_loader), model.evaluate(validation_loader)
```




    (0.39349932589025605, 0.42693415356237674)


