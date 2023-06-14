import torch
import utils
import model

device = 'cuda' if torch.cuda.is_available() else 'cpu'

print("Using "+device+" device.")

with open('./dataset/articles.txt', 'r', encoding='utf-8') as f:
    text = f.read()

print("Lenght of the Dataset:", len(text))

tok = utils.Tokenizer(text)

print(f"Vocab size: {len(tok.vocab)}")
print(f"Vocab: {tok.vocab}")

data = torch.tensor(tok.encode(text), dtype=torch.long)

n = int(0.9*len(data))
train_data = data[:n]
test_data = data[n:]

block_size = 64
batch_size = 8

def get_batch(split = "train"):
    data = train_data if split == "train" else test_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    x, y = x.to(device), y.to(device)

    return x, y

xb, yb = get_batch()
print(f'inputs: {xb.shape}')
print(xb)
print(f'targets: {yb.shape}')
print(yb)
print('--------------')

model = model.BigramLanguageModel(len(tok.vocab), block_size)
m = model.to(device)
out, loss = model(xb, yb)
print(out.shape)
print(loss)

optimizer = torch.optim.AdamW(m.parameters(), lr=1e-3)

training_steps = 10000
log_step = 1000
for step in range(training_steps):

    # Sample a batch of training data
    xb, yb = get_batch()

    # Actual training
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    if step%1000 == 0:
        print(f"[{step/log_step}/{training_steps//log_step}] Loss: {loss.item()}")

inputs = torch.tensor([tok.encode("ART")], dtype=torch.long)
print("inputs: ", inputs)
out = m.generate(inputs, 3200)
print(out)
print(tok.decode(out[0].tolist()))