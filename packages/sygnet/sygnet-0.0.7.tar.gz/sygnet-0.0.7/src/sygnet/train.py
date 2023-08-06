### TRAINING FUNCTIONS
from .requirements import *

logger = logging.getLogger(__name__)

def train_basic(
    training_data, 
    generator, 
    discriminator,
    epochs, 
    device,
    batch_size,
    learning_rate,
    use_tensorboard
    ):
    """Training function for basic GAN method

    Args:
        training_data (Dataset): Real data used to train GAN
        generator (nn.Module): Generator model object
        discriminator (nn.Module): Discriminator model object
        epochs (int): Number of training epochs
        device (str): Either 'cuda' for GPU training, or 'cpu'.
        batch_size (int): Number of training observations per batch
        learning_rate (float): The learning rate for the Adam optimizer (default = 0.0001)
        use_tensorboard (boolean): If True, creates tensorboard output capturing key training metrics (default = True)

    Note: 
        The generator (and discriminator) model is modified in-place so this is not returned by the function

    Returns:
        generator_losses (list), discriminator_losses (list): lists of losses at the batch-level

    """

    data_loader = DataLoader(dataset = training_data, batch_size=batch_size, shuffle=True)

    if use_tensorboard:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(f'outputs/run_gan_{datetime.now()}')

    # Models
    discriminator_model = discriminator.to(device)
    generator_model = generator.to(device)

    # Optimizers
    generator_optimizer = torch.optim.Adam(generator_model.parameters(), lr=learning_rate)
    discriminator_optimizer = torch.optim.Adam(discriminator_model.parameters(), lr=learning_rate)

    # Loss recording
    generator_losses = []
    discriminator_losses = []

    # Define loss function
    loss = nn.BCELoss()

    # Training loop
    tbar = trange(epochs, desc="Epoch")
    for epoch in tbar:
        logger.debug("Epoch: "+str(epoch))
         
        for i, (features, labels) in enumerate(data_loader):

            logger.debug("Batch: "+str(i))

            generator_optimizer.zero_grad()

            gen_obs = features.size(dim=0)
            gen_cols = features.size(dim=1)

            noisy_input = torch.rand(size=(gen_obs, gen_cols))
            noisy_input = noisy_input.to(device)
            generated_data = generator_model(noisy_input).to(device)

            true_data = features.to(device)
            true_labels = labels.to(device)

            logger.debug("BATCHSTEP: Training the generator")
            generator_discriminator_out = discriminator_model(generated_data)
            generator_loss = loss(generator_discriminator_out, true_labels)
            generator_loss.backward()
            generator_optimizer.step()

            logger.debug("BATCHSTEP: Training discriminator on true data")
            discriminator_optimizer.zero_grad()
            true_discriminator_out = discriminator_model(true_data)
            true_discriminator_loss = loss(true_discriminator_out, true_labels)

            logger.debug("BATCHSTEP: Training discriminator on fake data")
            generator_discriminator_out = discriminator_model(generated_data.detach())  #  Detach to break out of grad. calc.
            generator_discriminator_loss = loss(generator_discriminator_out, torch.zeros(gen_obs, 1).to(device))
            discriminator_loss = (true_discriminator_loss + generator_discriminator_loss) / 2
            discriminator_loss.backward()
            discriminator_optimizer.step()

            generator_losses.append(generator_loss.item())
            discriminator_losses.append(true_discriminator_loss.item())

        if use_tensorboard:
            writer.add_scalar('Generator loss', generator_loss, global_step=epoch)
            writer.add_scalar('True Discriminator loss', true_discriminator_loss, global_step=epoch)

        logger.info(" Epoch %s summary: Generator loss: %s; True discriminator loss = %s; Training loss: %s" % (epoch, round(generator_loss.item(),5), round(true_discriminator_loss.item(),5), round(generator_discriminator_loss.item(),5)))

    return generator_losses, discriminator_losses

def train_wgan(
    training_data, 
    generator, 
    critic,
    epochs, 
    device,
    batch_size,
    learning_rate,
    adam_betas,
    lmbda,
    use_tensorboard
    ):
    """Training function for Wasserstein-GP GAN method

    Args:
        training_data (Dataset): Real data used to train GAN
        generator (nn.Module): Generator model object
        critic (nn.Module): Critic model object
        epochs (int): Number of training epochs
        device (str): Either 'cuda' for GPU training, or 'cpu'.
        batch_size (int): Number of training observations per batch
        learning_rate (float): The learning rate for the Adam optimizer
        adam_betas (tuple): The beta parameters for the Adam optimizer
        lmbda (float): Scalar penalty term for applying gradient penalty as part of Wasserstein loss
        use_tensorboard (boolean): If True, creates tensorboard output capturing key training metrics (default = True)

    Note: 
        The generator and critic models are modified in-place so this is not returned by the function

    Returns:
        generator_losses (list), critic_losses (list): lists of losses at the batch-level

    """

    data_loader = DataLoader(dataset = training_data, batch_size=batch_size, shuffle=True)

    if use_tensorboard:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(f'outputs/run_wgan_{datetime.now()}')
    # Models
    critic_model = critic.to(device)
    generator_model = generator.to(device)

    # Optimizers
    generator_optimizer = torch.optim.Adam(generator_model.parameters(), lr=learning_rate, betas=adam_betas)
    critic_optimizer = torch.optim.Adam(critic_model.parameters(), lr=learning_rate, betas=adam_betas)

    # Loss recording
    generator_losses = []
    critic_losses = []

    # Training loop
    tbar = trange(epochs, desc="Epoch")
    for epoch in tbar:

        for i, (features, _) in enumerate(data_loader):
            
            # Get info on batches
            gen_obs = features.size(dim=0)
            gen_cols = features.size(dim=1)

            real_data = features.to(device)
            # real_labels = labels.to(device)

            ## Sort out the critic
            # Zero gradients and get critic scores
            generator_model.zero_grad()
            critic_model.zero_grad()

            critic_score_real = critic_model(real_data)
            
            fake_input = torch.rand(size=(gen_obs, gen_cols))
            fake_input = fake_input.to(device)
            fake_data = generator_model(fake_input).to(device)

            critic_score_fake = critic_model(fake_data)

            # Calculate gradient penalty
            eps_shape = [gen_obs] + [1]*(len(features.shape)-1)
            eps = torch.rand(eps_shape).to(device)
            mixed_data = eps*real_data + (1-eps)*fake_data
            mixed_output = critic_model(mixed_data)

            grad = torch.autograd.grad(
                outputs = mixed_output,
                inputs = mixed_data,
                grad_outputs = torch.ones_like(mixed_output),
                create_graph = True,
                retain_graph = True,
                only_inputs=True,
                allow_unused=True
            )[0]

            critic_grad_penalty = ((grad.norm(2, dim=1) -1)**2)

            error_critic = (critic_score_fake - critic_score_real).mean() + critic_grad_penalty.mean()*lmbda
            error_critic.backward()
            critic_optimizer.step()

            critic_losses.append(error_critic.item())

            ## Sort out the generator
            # Re-zero gradients
            generator_model.zero_grad()
            critic_model.zero_grad()
            # Refresh random fake data
            fake_input2 = torch.rand(size=(gen_obs, gen_cols))
            fake_input2 = fake_input2.to(device)
            fake_data2 = generator_model(fake_input2).to(device)

            neg_critic_score_fake = -critic_model(fake_data2)
            error_gen = neg_critic_score_fake.mean()
            error_gen.backward()
            generator_optimizer.step()

            generator_losses.append(error_gen.item())
        
        if use_tensorboard:
            writer.add_scalar('Critic loss', critic_losses[-1], global_step=epoch)
            writer.add_scalar('Generator loss', generator_losses[-1], global_step=epoch)

        logger.info("Epoch %s summary: Generator loss: %s; Critic loss = %s" % (epoch, round(generator_losses[-1],5), round(critic_losses[-1],5)))
        tbar.set_postfix(loss = critic_losses[-1])
    return generator_losses, critic_losses

def train_conditional(
    training_data, 
    generator, 
    critic,
    epochs, 
    device,
    batch_size,
    learning_rate,
    adam_betas,
    lmbda,
    use_tensorboard
    ):
    """Training function for conditional GAN (using Wasserstein loss)

    Args:
        training_data (Dataset): Real data used to train GAN
        generator (nn.Module): Generator model object
        critic (nn.Module): Critic model object
        epochs (int): Number of training epochs
        device (str): Either 'cuda' for GPU training, or 'cpu'.
        batch_size (int): Number of training observations per batch
        learning_rate (float): The learning rate for the Adam optimizer
        adam_betas (tuple): The beta parameters for the Adam optimizer
        lmbda (float): Scalar penalty term for applying gradient penalty as part of Wasserstein loss
        use_tensorboard (boolean): If True, creates tensorboard output capturing key training metrics (default = True)

    Note: 
        The generator and critic models are modified in-place so this is not returned by the function

    Returns:
        generator_losses (list), critic_losses (list): lists of losses at the batch-level

    """

    data_loader = DataLoader(dataset = training_data, batch_size=batch_size, shuffle=True)

    if use_tensorboard:
        from torch.utils.tensorboard import SummaryWriter
        writer = SummaryWriter(f'outputs/run_cond_wgan_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}')
    
    # Send models to device
    critic_model = critic.to(device)
    generator_model = generator.to(device)

    # Optimizers
    generator_optimizer = torch.optim.Adam(generator_model.parameters(), lr=learning_rate, betas=adam_betas)
    critic_optimizer = torch.optim.Adam(critic_model.parameters(), lr=learning_rate, betas=adam_betas)

    # Loss recording
    generator_losses = []
    critic_losses = []

    # Training loop
    tbar = trange(epochs, desc="Epoch")
    for epoch in tbar:
         
        for i, (features, labels) in enumerate(data_loader):
            
            # Get info on batches
            gen_obs = features.size(dim=0)
            gen_cols = features.size(dim=1)

            real_data = features.to(device)
            real_labels = labels.to(device)

            ## Sort out the critic
            # Zero gradients and get critic scores
            generator_model.zero_grad()
            critic_model.zero_grad()

            critic_score_real = critic_model(real_data, real_labels)
            
            fake_input = torch.rand(size=(gen_obs, gen_cols))
            fake_input = fake_input.to(device)
            fake_data = generator_model(fake_input, real_labels).to(device)

            critic_score_fake = critic_model(fake_data, real_labels)

            # Calculate gradient penalty
            eps_shape = [gen_obs] + [1]*(len(features.shape) -1)
            eps = torch.rand(eps_shape).to(device)
            mixed_data = eps*real_data + (1-eps)*fake_data
            mixed_output = critic_model(mixed_data, real_labels)

            grad = torch.autograd.grad(
                outputs = mixed_output,
                inputs = mixed_data,
                grad_outputs = torch.ones_like(mixed_output),
                create_graph = True,
                retain_graph = True,
                only_inputs=True,
                allow_unused=True
            )[0]

            critic_grad_penalty = ((grad.norm(2, dim=1) -1)**2)

            error_critic = (critic_score_fake - critic_score_real).mean() + critic_grad_penalty.mean()*lmbda
            error_critic.backward()
            critic_optimizer.step()

            critic_losses.append(error_critic.item())

            ## Sort out the generator
            # Re-zero gradients
            generator_model.zero_grad()
            critic_model.zero_grad()
            # Refresh random fake data
            fake_input2 = torch.rand(size=(gen_obs, gen_cols))
            fake_input2 = fake_input2.to(device)
            fake_data2 = generator_model(fake_input2, real_labels).to(device)

            neg_critic_score_fake = -critic_model(fake_data2, real_labels)
            error_gen = neg_critic_score_fake.mean()
            error_gen.backward()
            generator_optimizer.step()

            generator_losses.append(error_gen.item())

        if use_tensorboard:
            writer.add_scalar('Critic loss', critic_losses[-1], global_step=epoch)
            writer.add_scalar('Generator loss', generator_losses[-1], global_step=epoch)

        logger.info("Epoch %s summary: Generator loss: %s; Critic loss = %s" % (epoch, round(generator_losses[-1],5), round(critic_losses[-1],5)))
        tbar.set_postfix(loss = critic_losses[-1])

    return generator_losses, critic_losses
